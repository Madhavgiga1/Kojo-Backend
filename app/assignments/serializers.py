from rest_framework import serializers
from core.models import (Assignment,AssignmentSubmission)


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields ='__all__'
        read_only_fields = ['created_by']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at']