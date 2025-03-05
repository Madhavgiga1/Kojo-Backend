from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from core.models import Student,Quiz, Question, QuestionOption, QuizAttempt, StudentSelectedQuestionOption,Teacher
from .serializers import (
    QuizSerializer, QuestionSerializer, QuizAttemptSerializer, QuestionOptionSerializer,StudentSelectedOptionSerializer
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


class QuestionView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            # Get quizzes created by this teacher
            quizzes = Quiz.objects.filter(teacher=teacher)
            # Get questions from those quizzes
            return Question.objects.filter(quiz__in=quizzes)
        return Question.objects.none()

class QuestionOptionView(generics.ListCreateAPIView):
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsTeacher]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            # Get quizzes created by this teacher
            quizzes = Quiz.objects.filter(teacher=teacher)
            # Get questions from those quizzes
            questions = Question.objects.filter(quiz__in=quizzes)
            # Get options for those questions
            return QuestionOption.objects.filter(related_question__in=questions)
        return QuestionOption.objects.none()
        
#this is viewset for getting final quiz submissions that are officially recorded
class QuizSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving quiz attempts by students.
    Students can only see their own quiz attempts.
    """
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'quiz_attempt_code'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            # Students see only their own submissions
            try:
                student = Student.objects.get(user=user)
                return QuizAttempt.objects.filter(related_student=student)
            except Student.DoesNotExist:
                return QuizAttempt.objects.none()
        else:
            # Empty queryset for non-students (will be handled in permission check)
            return QuizAttempt.objects.none()
    
    def list(self, request, *args, **kwargs):
        # Check if user is a student
        if request.user.role != 'student':
            return Response(
                {"error": "Only students can view quiz attempts"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        # Check if user is a student
        if request.user.role != 'student':
            return Response(
                {"error": "Only students can view quiz attempts"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)


#use this method for student to submit their answer for a particular option
class QuizQuestionAnswerView(generics.CreateAPIView):
    serializer_class = StudentSelectedOptionSerializer
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