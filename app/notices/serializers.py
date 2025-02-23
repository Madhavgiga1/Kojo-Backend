from rest_framework import serializers 

from core.models import Notices

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notices
        fields='__all__'
        read_only_fields=['created_by']