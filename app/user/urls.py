from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    StudentRegistrationAPIView,
    TeacherRegistrationAPIView,
    UserProfileAPIView,
    PasswordChangeView,
    # StudentViewSet,
    # TeacherViewSet
)

router = DefaultRouter()
# router.register('students', StudentViewSet, basename='student')
# router.register('teachers', TeacherViewSet, basename='teacher')

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Registration endpoints
    path('register/student/', StudentRegistrationAPIView.as_view(), name='register_student'),
    path('register/teacher/', TeacherRegistrationAPIView.as_view(), name='register_teacher'),
    
    # User profile endpoints
    path('profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # ViewSet routes
    #path('', include(router.urls)),
]