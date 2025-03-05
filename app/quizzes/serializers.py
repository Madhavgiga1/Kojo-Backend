from rest_framework import serializers
from core.models import Quiz, Question, QuestionOption, QuizAttempt, StudentSelectedQuestionOption,Section,Student,Teacher,Subject
from django.utils import timezone

class QuestionOptionSerializer(serializers.ModelSerializer):
    question_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = QuestionOption
        fields = ['option_code', 'question_code', 'text', 'is_correct']
        read_only_fields = ['option_code']
    
    def create(self, validated_data):
        import uuid
        
        # Get question by code
        question_code = validated_data.pop('question_code')
        try:
            question = Question.objects.get(question_code=question_code)
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_code": "Question not found"})
        
        # Create option with generated UUID
        option = QuestionOption.objects.create(
            option_code=uuid.uuid4(),
            related_question=question,
            **validated_data
        )
        
        # If this option is marked correct, update the question's correct_option_code
        if validated_data.get('is_correct', False):
            question.correct_option_code = option.option_code
            question.save()
            
        return option

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField(read_only=True)
    quiz_id = serializers.IntegerField(write_only=True)
    question_code = serializers.CharField(required=False)
    
    class Meta:
        model = Question
        fields = ['question_code', 'quiz_id', 'question_text', 'question_type', 
                  'marks', 'order', 'options']
    
    def get_options(self, obj):
        options = QuestionOption.objects.filter(related_question=obj)
        return QuestionOptionSerializer(options, many=True).data
    
    def create(self, validated_data):
        import uuid
        
        # Extract quiz_id to get the quiz object
        quiz_id = validated_data.pop('quiz_id')
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError({"quiz_id": "Quiz not found"})
        
        # Generate UUID if not provided
        if 'question_code' not in validated_data or not validated_data['question_code']:
            validated_data['question_code'] = str(uuid.uuid4())
            
        # Create new question
        question = Question.objects.create(
            quiz=quiz,
            **validated_data
        )
        
        return question

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    quiz_subject_code=serializers.CharField(write_only=True)
    teacher_identification_number=serializers.CharField(write_only=True)
    sections = serializers.ListField(
        child=serializers.CharField(max_length=10),
        write_only=True
    )
    class Meta:
        model = Quiz
        fields = [
            'id', 'quiz_name', 'quiz_description', 'quiz_subject_code', 'sections', 
            'teacher_identification_number', 'total_marks', 'time_limit_minutes', 'instructions',
            'due_date', 'start_time', 'end_time', 'is_proctored', 
            'created_at', 'questions', 'is_active'
        ]
        write_only_fields = ['sections','quiz_subject','sections','teacher_identification_number']
        read_only_fields = ['created_at', 'is_active']

    def create(self,validated_data):
        quiz_subject_code=validated_data.pop('quiz_subject_code')
        teacher_identification_number=validated_data.pop('teacher_identification_number')
        sections=validated_data.pop('sections')

        try:
            teacher = Teacher.objects.get(user__identification_number=teacher_identification_number)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({"teacher_identification_number": "Teacher not found"})

        
        try:
            subject = Subject.objects.get(subject_code=quiz_subject_code)
        except Subject.DoesNotExist:
            raise serializers.ValidationError({"quiz_subject_code": "Subject not found"})

        # Validate and get the sections
        section_objects = []
        for section_code in sections:
            try:
                section = Section.objects.get(section_code=section_code)
                section_objects.append(section)
            except Section.DoesNotExist:
                raise serializers.ValidationError({"sections": f"Section with code {section_code} not found"})

        # Create the quiz
        quiz = Quiz.objects.create(
            quiz_subject=subject,
            teacher=teacher,
            **validated_data
        )

        # Add sections to the quiz
        quiz.sections.set(section_objects)
        return quiz


class StudentSelectedOptionSerializer(serializers.ModelSerializer):
    quiz_attempt_code=serializers.CharField(max_length=50,write_only=True)
    question_code=serializers.CharField(max_length=50,write_only=True)
    selected_option_code=serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model = StudentSelectedQuestionOption
        fields = [
            'id','quiz_attempt_code', 'question_code', 'selected_option_code', 
            
        ]
        read_only_fields=['id']
        extra_kwargs = {
            'quiz_attempt_code': {'write_only': True},
            'question_code': {'write_only': True},
            'selected_option_code': {'write_only': True}
        }
        
    def create(self,validated_data):
       
        question_code=validated_data.pop('question_code') 
        quiz_attempt_code=validated_data.pop('quiz_attempt_code')
        selected_option_code=validated_data.pop('selected_option_code')
        question=Question.objects.get(question_code=question_code)
        quiz_attempt=QuizAttempt.objects.get(quiz_attempt_code=quiz_attempt_code)
        selected_option=QuestionOption.objects.get(selected_option_code=selected_option_code)
        score=0
        if(question.correct_option_code==selected_option_code):
            score=question.marks
        return StudentSelectedQuestionOption.objects.create(
            quiz_attempt=quiz_attempt,
            question=question,
            selected_option=selected_option,
            marks_awarded=score
        )

#only for reading 

class QuizAttemptSerializer(serializers.ModelSerializer):
    student_identification_number = serializers.CharField(write_only=True, required=False)
    quiz = serializers.PrimaryKeyRelatedField(source='related_quiz', read_only=True)
    quiz_name = serializers.CharField(source='related_quiz.quiz_name', read_only=True)
    start_time = serializers.DateTimeField(source='started_at', read_only=True)
    end_time = serializers.DateTimeField(source='ended_at', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'quiz_attempt_code', 'student_identification_number', 'quiz', 'quiz_name', 
            'start_time', 'end_time', 'is_completed', 'marks_obtained'
        ]
        read_only_fields = ['quiz_attempt_code', 'quiz', 'quiz_name', 'start_time', 
                           'end_time', 'is_completed', 'marks_obtained']
# class ProctoringImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProctoringImage
#         fields = ['id', 'quiz_attempt', 'image', 'timestamp', 'flagged', 'notes']
#         read_only_fields = ['timestamp', 'flagged', 'notes']  # These are set by teachers/admins