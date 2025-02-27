from django.urls import (path,include)
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet,AssignmentSubmissionViewSet

router = DefaultRouter()
app_name='assignments'
router.register('', AssignmentViewSet)
router.register('', AssignmentSubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]