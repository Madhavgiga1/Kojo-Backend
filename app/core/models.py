from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,  # Add this import
    BaseUserManager
)
import uuid
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, identification_number, password, **extra_fields):
        if not identification_number:
            raise ValueError('ID number must be set')
        user = self.model(identification_number=identification_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, identification_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'student')  # Set a default role for superusers
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(identification_number, password, **extra_fields)

# Make User inherit from both AbstractBaseUser and PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    identification_number = models.CharField(max_length=15, primary_key=True)
    ROLES = (
        ('teacher', 'Teacher'),
        ('student', 'Student')
    )
    role = models.CharField(max_length=10, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'identification_number'
    REQUIRED_FIELDS = ['role']

    def __str__(self) -> str:
        return self.identification_number

#programs like BTech, MTech, MBA
class Program(models.Model):
    program_code=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=100)

#specialization branches like CSE, ECE, MECH
class SpecializationBranch(models.Model):
    program=models.ForeignKey(Program,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    specialization_branch_code=models.CharField(max_length=20,primary_key=True)
    total_credits=models.IntegerField(blank=True)

#sections like IT1,IT2,IT3
class Section(models.Model):
    section_code=models.CharField(max_length=20,primary_key=True,default='IT-E')
    specialization_branch=models.ForeignKey(SpecializationBranch,on_delete=models.CASCADE)
    total_students=models.IntegerField(blank=True)


class Student(models.Model):

    user=models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True)
    first_name=models.CharField(max_length=100,blank=False)
    last_name=models.CharField(max_length=100,blank=False)
    batch=models.CharField(max_length=4)
    section=models.ForeignKey(Section,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.user.role == 'student':
            raise ValueError('User must have student role')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.user.identification_number}-{self.first_name}-{self.last_name}"
    
class Teacher(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    specialization_branch = models.ForeignKey(SpecializationBranch,on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.user.role == 'teacher':
            raise ValueError('User must have teacher role')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Teacher: {self.user.identification_number}-{self.first_name}-{self.last_name}"
    
class Subject(models.Model):
    
    subject_code=models.CharField(max_length=10,primary_key=True,default='IT2101')
    specialization_branch=models.ForeignKey(SpecializationBranch,on_delete=models.CASCADE)
    subject_name=models.CharField(max_length=100)
    credits=models.IntegerField(blank=True)
    def __str__(self):
        return self.subject_code
    
def get_submission_path(instance, filename):
    # instance is the AssignmentSubmission instance
    # Create path: submissions/section_name/student_id/filename
    return f'submissions/{instance.student.section}/{instance.student.user.identification_number}/{filename}'



class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=15)  # e.g., "2023-2024"
    semester = models.IntegerField()

    class Meta:
        unique_together = ['teacher', 'section', 'subject', 'academic_year', 'semester']

    def __str__(self):
        return f'{self.teacher} - {self.subject} - {self.section}'

def get_assignment_path(instance, filename):
    return f'assignments/{instance.section}/{instance.name}/{filename}'
class Assignment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
    total_marks = models.IntegerField(blank=True)
    due_date = models.DateField()
    assignment_pdf = models.FileField(upload_to=get_assignment_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}-{self.section}'

class AssignmentSubmission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    marks = models.IntegerField(blank=True, null=True)  # Added null=True since it might be graded later
    submission_pdf = models.FileField(upload_to=get_submission_path)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student}-{self.assignment}'

    class Meta:
        # Optionally add unique constraint to prevent multiple submissions
        unique_together = ['student', 'assignment']

class Notices(models.Model):
    title=models.CharField(max_length=100,blank=False)
    description=models.TextField(blank=False)
    created_at=models.DateTimeField(auto_now_add=True)
    section=models.ManyToManyField(Section)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)

def question_image_path(instance, filename):
    # Upload path: quiz_images/quiz_id/question_id/filename
    return f'quiz_images/quiz_{instance.quiz.id}/question_{instance.id}/{filename}'

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
        return self.quiz_name
        
    @property
    def is_active(self):
        now = timezone.now()
        return now >= self.start_time and now <= self.end_time
class Question(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        
    )
    question_code=models.UUIDField(primary_key=True,editable=False, default=uuid.uuid4)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    image = models.ImageField(upload_to=question_image_path, blank=True, null=True)
    correct_option_code=models.UUIDField(blank=True)
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
class QuestionOption(models.Model):
    option_code=models.UUIDField(primary_key=True,editable=False, default=uuid.uuid4)
    related_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField(blank=False)
    # is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text
    
class QuizAttempt(models.Model):
    quiz_attempt_code=models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
    related_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    related_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    marks_obtained = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.related_student} - {self.related_quiz}"
        
    class Meta:
        unique_together = ['related_student', 'related_quiz']  # One attempt per student per quiz
        
    @property
    def duration(self):
        if self.ended_at:
            return self.ended_at - self.started_at
        return None

    def get_total_questions(self):
        """Get the total number of questions in the quiz."""
        return self.related_quiz.questions.count()
    
    def get_answered_questions(self):
        """Get the number of questions answered in this attempt."""
        return self.answers.count()
    
    def get_correct_answers(self):
        """Get the number of correctly answered questions."""
        return self.answers.filter(selected_option__is_correct=True).count()
    
    
    def get_score(self):
        selected_answers=self.answers.all()
        score=0
        for answer in selected_answers:
            score+=(answer.marks_awarded)
        return score
    

class StudentSelectedQuestionOption(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    marks_awarded = models.PositiveIntegerField(default=0)
     
    
    class Meta:
        unique_together = ['quiz_attempt', 'question']  # One answer per question per attempt

  

# Proctoring system model
"""class ProctoringImage(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='proctoring_images')
    image = models.ImageField(upload_to='proctoring_images/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(default=False)  # Flag suspicious activity
    notes = models.TextField(blank=True)  # Notes on suspicious activity
    
    def __str__(self):
        return f"Proctoring image for {self.quiz_attempt} at {self.timestamp}"
        """
    
