# serializers.py
from rest_framework import serializers
from core.models import Assignment, AssignmentSubmission, Teacher, Section, Subject

# Updated AssignmentSerializer with date field customization
from rest_framework import serializers
from core.models import Assignment, Teacher, Section, Subject,Student,AssignmentSubmission
from drf_spectacular.utils import extend_schema_field, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class AssignmentSerializer(serializers.ModelSerializer):
    section_code = serializers.CharField(max_length=20, write_only=True)
    subject_code = serializers.CharField(max_length=10, write_only=True)
    
    # Enhanced date field with format specification for the date picker
    due_date = serializers.DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'],
        help_text="Assignment due date (format: YYYY-MM-DD)"
    )
    
    # Add these fields for read operations
    section_name = serializers.CharField(source='section.section_code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'name', 'description', 'due_date', 'section_code', 'subject_code',
            'section_name', 'subject_name', 'teacher_name',
            'assignment_pdf', 'total_marks', 'created_at'
        ]
        read_only_fields = ['teacher', 'created_at', 'section_name', 'subject_name', 'teacher_name']
        
        # Add schema examples for Spectacular
        examples = [
            OpenApiExample(
                'Assignment Example',
                value={
                    'name': 'Midterm Project',
                    'description': 'Create a simple Django application',
                    'due_date': '2023-10-30',
                    'section_code': 'IT-E',
                    'subject_code': 'IT2101',
                    'total_marks': 100
                },
                request_only=True,
            ),
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        teacher = Teacher.objects.get(user=user)
        
        # Extract and remove section_code from validated_data
        section_code = validated_data.pop('section_code')
        try:
            section = Section.objects.get(section_code=section_code)
        except Section.DoesNotExist:
            raise serializers.ValidationError({"section_code": "Section not found"})
        
        # Extract and remove subject_code from validated_data
        subject_code = validated_data.pop('subject_code')
        try:
            subject = Subject.objects.get(subject_code=subject_code)
        except Subject.DoesNotExist:
            raise serializers.ValidationError({"subject_code": "Subject not found"})
        
        # Create the assignment with the teacher, section and subject
        return Assignment.objects.create(
            teacher=teacher,
            section=section,
            subject=subject,
            **validated_data
        )
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_id = serializers.CharField(write_only=True)

    
    class Meta:
        model = AssignmentSubmission
        fields = ['student','marks', 'submission_pdf', 'submitted_at','assignment_id']
        read_only_fields = ['student', 'submitted_at','marks']
        extra_kwargs={
            'assignment_id': {'write_only': True}
        }
    
    def create(self,validated_data):
        user = self.context['request'].user
        student = Student.objects.get(user=user)
        
        # Extract and remove assignment_id from validated_data
        assignment_id = validated_data.pop('assignment_id')

        try:
            assignment = Assignment.objects.get(pk=assignment_id)
        except Assignment.DoesNotExist:
            raise serializers.ValidationError({"assignment_id": "Assignment not found"})
        
        # Create the assignment submission with the student and assignment
        return AssignmentSubmission.objects.create(
            student=student,
            assignment=assignment,
            **validated_data
        )
    

"""
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
"""