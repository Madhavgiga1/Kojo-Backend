from rest_framework.urls import (path,include)
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet,AssignmentSubmissionViewSet

router = DefaultRouter()

router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', AssignmentSubmissionViewSet, basename='submission')

urlpatterns = [
    path('api/', include(router.urls)),
]