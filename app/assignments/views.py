from django.shortcuts import render
from rest_framework import viewsets 
from core.models import (
    Assignment,
    AssignmentSubmission,
    TeachingAssignment,
)
from .serializers import(
    AssignmentSerializer,
)
class AssignmentViewset(viewsets.modelviewset):
    queryset=Assignment.objects.all()
    serializer_class=AssignmentSerializer