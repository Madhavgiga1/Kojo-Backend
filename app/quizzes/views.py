from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum
from core.models import Student,Teacher,Quiz, Question, QuestionOption, QuizAttempt, StudentAnswer, ProctoringImage
from .serializers import (
    QuizSerializer, QuestionSerializer, QuizAttemptSerializer, 
    StudentAnswerSerializer, ProctoringImageSerializer
)

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
        student = Student.objects.get(user=request.user)
        
        # Check if quiz is active
        if not quiz.is_active:
            return Response({"error": "Quiz is not currently available"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student already has an attempt
        existing_attempt = QuizAttempt.objects.filter(student=student, quiz=quiz, is_completed=False).first()
        if existing_attempt:
            serializer = QuizAttemptSerializer(existing_attempt)
            return Response(serializer.data)
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(student=student, quiz=quiz)
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit_attempt(self, request, pk=None):
        """Submit a completed quiz attempt"""
        quiz = self.get_object()
        student = Student.objects.get(user=request.user)
        
        try:
            attempt = QuizAttempt.objects.get(student=student, quiz=quiz, is_completed=False)
        except QuizAttempt.DoesNotExist:
            return Response({"error": "No active quiz attempt found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Calculate score
        total_score = StudentAnswer.objects.filter(quiz_attempt=attempt).aggregate(Sum('marks_awarded'))
        attempt.marks_obtained = total_score['marks_awarded__sum'] or 0
        attempt.end_time = timezone.now()
        attempt.is_completed = True
        attempt.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)

class StudentAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            student = Student.objects.get(user=user)
            return StudentAnswer.objects.filter(quiz_attempt__student=student)
        return StudentAnswer.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Auto-grade for multiple choice and true/false questions
        data = request.data
        attempt_id = data.get('quiz_attempt')
        question_id = data.get('question')
        selected_option_id = data.get('selected_option')
        
        # Check if answer already exists (update if it does)
        existing = StudentAnswer.objects.filter(quiz_attempt_id=attempt_id, question_id=question_id).first()
        
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

class ProctoringImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProctoringImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            # Teachers can see proctoring images for quizzes they created
            return ProctoringImage.objects.filter(quiz_attempt__quiz__teacher=teacher)
        return ProctoringImage.objects.none()
    
    def create(self, request, *args, **kwargs):
        attempt_id = request.data.get('quiz_attempt')
        # Verify the attempt belongs to the current student
        if request.user.role == 'student':
            student = Student.objects.get(user=request.user)
            attempt = QuizAttempt.objects.filter(id=attempt_id, student=student).first()
            if not attempt:
                return Response({"error": "Unauthorized"}, 
                               status=status.HTTP_403_FORBIDDEN)
                
        return super().create(request, *args, **kwargs)