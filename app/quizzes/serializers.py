from rest_framework import serializers
from core.models import Quiz, Question, QuestionOption, QuizAttempt, StudentAnswer
#, ProctoringImage

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            'is_correct': {'write_only': True}  # Hide correct answer from students
        }

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'image', 'marks', 'order', 'options']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'name', 'description', 'subject', 'sections', 
            'teacher', 'total_marks', 'time_limit_minutes', 'instructions',
            'due_date', 'start_time', 'end_time', 'is_proctored', 
            'created_at', 'questions', 'is_active'
        ]
        read_only_fields = ['sections','subject','created_at', 'is_active']

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'quiz_attempt', 'question', 'selected_option', 
            'text_answer', 'is_correct', 'marks_awarded'
        ]
        extra_kwargs = {
            'is_correct': {'read_only': True},
            'marks_awarded': {'read_only': True}
        }

class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'quiz', 'start_time', 'end_time',
            'is_completed', 'marks_obtained', 'duration', 'answers'
        ]
        read_only_fields = ['start_time', 'end_time', 'is_completed', 'marks_obtained']

# class ProctoringImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProctoringImage
#         fields = ['id', 'quiz_attempt', 'image', 'timestamp', 'flagged', 'notes']
#         read_only_fields = ['timestamp', 'flagged', 'notes']  # These are set by teachers/admins