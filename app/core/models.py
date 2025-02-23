from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
    AbstractUser
)
# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, password, **extra_fields):
        if not id_number:
            raise ValueError('ID number must be set')
        user = self.model(identification_number=id_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, id_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(id_number, password, **extra_fields)
    

class User(AbstractBaseUser):
    identification_number=models.CharField(max_length=15,primary_key=True)
    ROLES=(
        ('teacher','Teacher'),
        ('student','Student')
    )
    role=models.CharField(max_length=10,choices=ROLES)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    date_joined=models.DateTimeField(auto_now_add=True)

    objects=CustomUserManager()

    username_field=identification_number
    REQUIRED_FIELDS=['role']

    def __str__(self) -> str:
        return self.identification_number

class Program(models.Model):
    program_code=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=100)

class SpecializationBranch(models.Model):
    program=models.ForeignKey(Program,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=10,primary_key=True)
    total_credits=models.IntegerField(blank=True)

class Section(models.Model):
    name=models.CharField(max_length=5)
    department=models.CharField(max_length=100)
    batch=models.CharField(max_length=4)
    total_students=models.IntegerField(blank=True)
    def __str__(self):
        return f"{self.department} {self.batch} {self.name}"

class Student(models.Model):

    user=models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True)
    department=models.CharField(max_length=100)
    batch=models.CharField(max_length=4)
    section=models.CharField(max_length=5)

    def save(self, *args, **kwargs):
        if not self.user.role == 'student':
            raise ValueError('User must have student role')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.user.identification_number}"
    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        if not self.user.role == 'teacher':
            raise ValueError('User must have teacher role')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Teacher: {self.user.id_number}"
    
class Subject(models.Model):
    
    code=models.CharField(max_length=10,primary_key=True)
    specialization_branch=models.ForeignKey(SpecializationBranch,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    department=models.CharField(max_length=100)
    credits=models.IntegerField(blank=True)
    def __str__(self):
        return self.name
    
def get_submission_path(instance, filename):
    # instance is the AssignmentSubmission instance
    # Create path: submissions/section_name/student_id/filename
    return f'submissions/{instance.student.section}/{instance.student.user.identification_number}/{filename}'



class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)  # e.g., "2023-2024"
    semester = models.IntegerField()

    class Meta:
        unique_together = ['teacher', 'section', 'subject', 'academic_year', 'semester']

    def __str__(self):
        return f'{self.teacher} - {self.subject} - {self.section}'

class Assignment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total_marks = models.IntegerField(blank=True)
    due_date = models.DateField()
    assignment_pdf = models.FileField(upload_to=f'assignments/{name}/{section}')
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

class Quiz(models.Model):
    name=models.CharField(max_length=150)
    description=models.TextField(blank=True)
    sections=models.ManyToManyField(Section)
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    total_marks=models.IntegerField(blank=True)
    due_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)

class QuizResponse(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE)
    marks_obtained=models.IntegerField(blank=False)
    submitted_at=models.DateTimeField(auto_now_add=True)

class Notices(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField(blank=False)
    created_at=models.DateTimeField(auto_now_add=True)
    sections=models.ManyToManyField(Section)
    teachers=models.ForeignKey(Teacher,on_delete=models.CASCADE)

    
