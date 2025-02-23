from rest_framework import viewsets,generics
from core.models import Notices
from .serializers import NoticeSerializer
from core.permissions import IsTeacher
from rest_framework.permissions import IsAuthenticated
class NoticeViewSet(viewsets.ModelViewSet):
    queryset=Notices.objects.all()
    serializer_class=NoticeSerializer

    def get_permissions(self):
        if(self.action in ['create','update','partial_update','destroy']):
            permission_classes=[IsTeacher]
        else:
            permission_classes=[IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        return self.queryset.filter(section=self.request.user.student.section)
    
