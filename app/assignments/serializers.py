from rest_framework import serializers
from core.models import (Assignment,AssignmentSubmission)


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_marks', 'created_by']
        read_only_fields = ['created_by']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'submission_content', 'submitted_at', 'marks_obtained']
        read_only_fields = ['student', 'submitted_at']