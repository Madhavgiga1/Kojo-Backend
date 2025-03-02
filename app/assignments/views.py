# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.permissions import IsTeacher, IsStudent
from core.models import Assignment, AssignmentSubmission, Student, Teacher, Section
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'teacher':
            # Teachers see assignments they created
            teacher = get_object_or_404(Teacher, user=user)
            return Assignment.objects.filter(teacher=teacher)
        elif user.role == 'student':
            # Students see assignments for their section
            student = get_object_or_404(Student, user=user)
            return Assignment.objects.filter(section=student.section)
        
        # Default empty queryset
        return Assignment.objects.none()

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsStudent]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            # Students see their own submissions
            student = get_object_or_404(Student, user=user)
            return AssignmentSubmission.objects.filter(student=student)
        elif user.role == 'teacher':
            # Teachers see submissions for assignments they created
            teacher = get_object_or_404(Teacher, user=user)
            return AssignmentSubmission.objects.filter(assignment__teacher=teacher)
        
        # Default empty queryset
        return AssignmentSubmission.objects.none()

