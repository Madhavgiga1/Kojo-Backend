from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, AssignmentSubmissionViewSet

router = DefaultRouter()

# Add basename parameter to fix the error
router.register('assignments', AssignmentViewSet, basename='assignment')
router.register('submissions', AssignmentSubmissionViewSet, basename='assignment-submission')

app_name = 'assignments'

urlpatterns = [
    path('', include(router.urls)),
]