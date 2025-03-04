from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from core.models import Student,Quiz, Question, QuestionOption, QuizAttempt, StudentSelectedQuestionOption,Teacher
from .serializers import (
    QuizSerializer, QuestionSerializer, QuizAttemptSerializer, QuestionOptionSerializer, StudentAnswerSerializer
)
from rest_framework import generics,mixins
from core.permissions import IsStudent,IsTeacher
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Teachers see all quizzes they created
            return Quiz.objects.filter(teacher=self.request.user.teacher)
        elif user.role == 'student':
            # Students see quizzes for their section
            student = Student.objects.get(user=user)
            return Quiz.objects.filter(sections=student.section)
        return Quiz.objects.none()
    
    @action(detail=True, methods=['post'])
    def start_attempt(self, request, pk=None):
        """Start a new quiz attempt"""
        quiz = self.get_object()
        user=request.user
        
        
        # Check if quiz is active
        if not quiz.is_active:
            return Response({"error": "Quiz is not currently available"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student already has an attempt
        # existing_attempt = QuizAttempt.objects.filter(student=student, quiz=quiz, is_completed=False).first()
        # if existing_attempt:
        #     serializer = QuizAttemptSerializer(existing_attempt)
        #     return Response(serializer.data)
        
        # Create new attempt
        if(user.role=='student'):
            student = Student.objects.get(user=user)
            attempt = QuizAttempt.objects.create(related_student=student, related_quiz=quiz)
            serializer = QuizAttemptSerializer(attempt)
            return Response(serializer.data)
        else:
            return Response({"error": "Only students can start quiz attempts"},status=status.HTTP_403_BAD_REQUEST) 


    @action(detail=True, methods=['post'])
    def submit_attempt(self, request, pk=None):
        """Submit a completed quiz attempt"""
        quiz = self.get_object()
        student = Student.objects.get(user=request.user)
        
        try:
            attempt = QuizAttempt.objects.get(related_student=student, related_quiz=quiz, is_completed=False)
        except QuizAttempt.DoesNotExist:
            return Response({"error": "No active quiz attempt found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Calculate score
        total_score = StudentAnswer.objects.filter(quiz_attempt=attempt).aggregate(Sum('marks_awarded'))
        attempt.marks_obtained = attempt.get_score()
        attempt.end_time = timezone.now()
        attempt.is_completed = True
        attempt.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)

class StudentAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAnswerSerializer
    

    def get_permissions(self):
        if(self.action in ['create']):
            permission_classes = [IsStudent]
        
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            student = Student.objects.get(user=user)
            return StudentSelectedQuestionOption.objects.filter(quiz_attempt__student=student)
        return StudentSelectedQuestionOption.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Auto-grade for multiple choice and true/false questions
        data = request.data
        attempt_id = data.get('quiz_attempt')
        question_id = data.get('question')
        selected_option_id = data.get('selected_option')
        
        # Check if answer already exists (update if it does)
        existing = StudentSelectedQuestionOption.objects.filter(quiz_attempt_id=attempt_id, question_id=question_id).first()
        
        question = Question.objects.get(id=question_id)
        is_correct = False
        marks_awarded = 0
        
        if question.question_type in ['multiple_choice', 'true_false'] and selected_option_id:
            option = QuestionOption.objects.get(id=selected_option_id)
            is_correct = option.is_correct
            marks_awarded = question.marks if is_correct else 0
        
        data.update({
            'is_correct': is_correct,
            'marks_awarded': marks_awarded
        })
        
        if existing:
            serializer = self.get_serializer(existing, data=data)
        else:
            serializer = self.get_serializer(data=data)
            
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class QuestionOptionView(generics.ListCreateAPIView):
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsTeacher]

    
class QuestionView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Teachers see all questions for quizzes they created
            teacher=Teacher.objects.get(user=user)
            return Question.objects.filter(teacher=teacher)
        else :
            return Response({"error": "Only teachers can create questions"},status=status.HTTP_403_BAD_REQUEST)
        
#this is viewset for getting final quiz submissions that are officially recorded
class QuizSubmissionViewSet(generics.ListAPIView,generics.RetrieveAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Teachers see all submissions for quizzes they created

            return Response({"error": "Only students can start quiz attempts"},status=status.HTTP_403_BAD_REQUEST)
        elif user.role == 'student':
            # Students see only their own submissions
            student = Student.objects.get(user=user)
            return QuizAttempt.objects.filter(related_student=student)
        return QuizAttempt.objects.none()
    


#use this method for student to submit their answer for a particular option
class QuizQuestionAnswerViewSet(generics.CreateAPIView):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsStudent]
    
 



        
# class ProctoringImageViewSet(viewsets.ModelViewSet):
#     serializer_class = ProctoringImageSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'teacher':
#             teacher = Teacher.objects.get(user=user)
#             # Teachers can see proctoring images for quizzes they created
#             return ProctoringImage.objects.filter(quiz_attempt__quiz__teacher=teacher)
#         return ProctoringImage.objects.none()
    
#     def create(self, request, *args, **kwargs):
#         attempt_id = request.data.get('quiz_attempt')
#         # Verify the attempt belongs to the current student
#         if request.user.role == 'student':
#             student = Student.objects.get(user=request.user)
#             attempt = QuizAttempt.objects.filter(id=attempt_id, student=student).first()
#             if not attempt:
#                 return Response({"error": "Unauthorized"}, 
#                                status=status.HTTP_403_FORBIDDEN)
                
#         return super().create(request, *args, **kwargs)