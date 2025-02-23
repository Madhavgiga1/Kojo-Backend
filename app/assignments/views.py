from django.shortcuts import render
from rest_framework import viewsets 
from core.permissions import IsTeacher, IsAuthenticated, IsStudent
from core.models import (
    Assignment,
    AssignmentSubmission,
    TeachingAssignment,
)
from .serializers import(
    AssignmentSerializer,
    AssignmentSubmissionSerializer
)
class AssignmentViewSet(viewsets.modelviewset):
    queryset=Assignment.objects.all()
    serializer_class=AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacher]
            #allows if IsTeacher is true
        else:
            permission_classes = [IsAuthenticated]  
            # Both teachers and students can view
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsStudent]
        elif self.action in ['update', 'partial_update']:  # For grading
            permission_classes = [IsTeacher]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.request.user.role == 'student':
            return AssignmentSubmission.objects.filter(student=self.request.user)
        return AssignmentSubmission.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)