from rest_framework import serializers
from core.models import (Assignment,AssignmentSubmission,TeachingAssignment,Subject,Teacher,Student)


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assignment
        fields='__all__'