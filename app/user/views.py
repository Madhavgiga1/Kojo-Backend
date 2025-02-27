from rest_framework import status, permissions, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate

from core.models import User, Teacher, Student
from .serializers import (
    UserSerializer, 
    StudentRegistrationSerializer, 
    TeacherRegistrationSerializer,
    StudentProfileSerializer,
    TeacherProfileSerializer,
    PasswordChangeSerializer
)

class LoginView(ObtainAuthToken):
    """
    API view for user login that returns an auth token.
    """
    def post(self, request, *args, **kwargs):
        identification_number = request.data.get('identification_number')
        password = request.data.get('password')
        
        if not identification_number or not password:
            return Response(
                {'error': 'Please provide both identification_number and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        
        user = authenticate(username=identification_number, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
       
        token, created = Token.objects.get_or_create(user=user)
        
        # Return token and user info
        user_data = {
            'identification_number': user.identification_number,
            'role': user.role
        }
        
        # Add role-specific info
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                user_data['name'] = f"{student.first_name} {student.last_name}"
            except Student.DoesNotExist:
                pass
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                user_data['name'] = f"{teacher.first_name} {teacher.last_name}"
            except Teacher.DoesNotExist:
                pass
        
        return Response({
            'token': token.key,
            'user': user_data
        })

class LogoutView(APIView):
    """
    API view for logging out a user (invalidating their token).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token to logout
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

class StudentRegistrationAPIView(generics.CreateAPIView):
    """API view that allows registering new student users"""
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=student.user)
        
        return Response({
            'token': token.key,
            'user': {
                'identification_number': student.user.identification_number,
                'role': student.user.role,
                'name': f"{student.first_name} {student.last_name}"
            }
        }, status=status.HTTP_201_CREATED)

class TeacherRegistrationAPIView(generics.CreateAPIView):
    """API view that allows registering new teacher users"""
    permission_classes = [permissions.AllowAny]
    serializer_class = TeacherRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=teacher.user)
        
        return Response({
            'token': token.key,
            'user': {
                'identification_number': teacher.user.identification_number,
                'role': teacher.user.role,
                'name': f"{teacher.first_name} {teacher.last_name}"
            }
        }, status=status.HTTP_201_CREATED)
    
# Add these view definitions to your views.py

class UserProfileAPIView(APIView):
    """API view for retrieving and updating user profiles"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'student':
            student = Student.objects.get(user=user)
            serializer = StudentProfileSerializer(student)
        elif user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            serializer = TeacherProfileSerializer(teacher)
        else:
            # Handle other user types or return basic user info
            serializer = UserSerializer(user)
            
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        
        if user.role == 'student':
            student = Student.objects.get(user=user)
            serializer = StudentProfileSerializer(student, data=request.data, partial=True)
        elif user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            serializer = TeacherProfileSerializer(teacher, data=request.data, partial=True)
        else:
            # Handle other user types
            serializer = UserSerializer(user, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    """API view for changing password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password changed successfully"}, 
                          status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class StudentViewSet(viewsets.ReadOnlyModelViewSet):
#     """ViewSet for viewing student details (primarily for teachers)"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = StudentProfileSerializer
    
#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'teacher':
#             # Teachers can see students in sections they teach
#             teacher = Teacher.objects.get(user=user)
#             # Get sections where this teacher has teaching assignments
#             teaching_sections = teacher.teachingassignment_set.values_list('section', flat=True)
#             return Student.objects.filter(section__in=teaching_sections)
        
#         # Students can only see themselves
#         if user.role == 'student':
#             return Student.objects.filter(user=user)
            
#         return Student.objects.none()

# class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
#     """ViewSet for viewing teacher details"""
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = TeacherProfileSerializer
    
#     def get_queryset(self):
#         # Everyone can see all teachers
#         return Teacher.objects.all()

# # UserProfileAPIView, PasswordChangeView, StudentViewSet, and TeacherViewSet remain the same
# # as in the previous example