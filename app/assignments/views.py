from django.shortcuts import render
from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsTeacher, IsStudent
from core.models import (
    Assignment,
    AssignmentSubmission,
)
from .serializers import(
    AssignmentSerializer,
    AssignmentSubmissionSerializer
)
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return self.queryset.filter(created_by=self.request.user)
        else:
            return self.queryset.filter(section=self.request.user.student.section)

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsStudent]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.role == 'student':
            return AssignmentSubmission.objects.filter(student=self.request.user)
        return AssignmentSubmission.objects.all()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)