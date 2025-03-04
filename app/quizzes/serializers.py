from rest_framework import serializers
from core.models import Quiz, Question, QuestionOption, QuizAttempt, StudentSelectedQuestionOption,Section,Student,Teacher,Subject
from django.utils import timezone
#, ProctoringImage

"""
class Quiz(models.Model):
    quiz_name = models.CharField(max_length=150)
    quiz_description = models.TextField(blank=True)
    quiz_subject = models.ForeignKey(Subject, on_delete=models.CASCADE) 
    sections = models.ManyToManyField(Section)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total_marks = models.IntegerField()
    time_limit_minutes = models.PositiveIntegerField(default=60)
    instructions = models.TextField(blank=True)
    due_date = models.DateField()
    start_time = models.DateTimeField()  # Time when quiz becomes available
    end_time = models.DateTimeField()    # Time when quiz is no longer available
    is_proctored = models.BooleanField(default=False)  # Whether proctoring is enabled
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
    @property
    def is_active(self):
        now = timezone.now()
        return now >= self.start_time and now <= self.end_time
class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    image = models.ImageField(upload_to=question_image_path, blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:30]}..."

class QuestionOption(models.Model):
    related_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text
class QuizAttempt(models.Model):
    related_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    marks_obtained = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.related_student} - {self.quiz}"
        
    class Meta:
        unique_together = ['related_student', 'quiz']  # One attempt per student per quiz
        
    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

class StudentAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)  # For short answer questions
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['quiz_attempt', 'question']  # One answer per question per attempt
"""
class QuestionOptionSerializer(serializers.ModelSerializer):
    associated_question_code=serializers.CharField(max_length=50,write_only=True)

    class Meta:
        model = QuestionOption
        fields = ['associated_question_code', 'text']
    
    def create(self,validated_data):
        question_code=validated_data.pop('associated_question_code')
        question=Question.objects.get(question_code=question_code)
        return QuestionOption.objects.create(related_question=question,**validated_data)

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    question_code=serializers.CharField(max_length=50,write_only=True)
    class Meta:
        model = Question
        fields = ['question_code', 'text', 'marks', 'options']
    
    def create(self, validated_data):
        question_code=validated_data.pop('question_code')
        options=validated_data.pop('options')
        question=Question.objects.get(question_code=question_code,**validated_data)

        for option in options:
            option_obj, created=QuestionOption.objects.get_or_create(
                related_question=question,
                **option
            )   
            question.options.add(option_obj)
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
            teacher = Teacher.objects.get(identification_number=teacher_identification_number)
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

class QuizAttemptSerializer(serializers.ModelSerializer):
    #answers = StudentSelectedOptionSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'quiz', 'start_time', 'end_time',
            'is_completed', 'marks_obtained', 'duration'
        ]
        read_only_fields = ['start_time', 'end_time', 'is_completed', 'marks_obtained']

# class ProctoringImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProctoringImage
#         fields = ['id', 'quiz_attempt', 'image', 'timestamp', 'flagged', 'notes']
#         read_only_fields = ['timestamp', 'flagged', 'notes']  # These are set by teachers/admins