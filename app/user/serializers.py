from rest_framework import serializers
from core.models import User, Teacher, Student, Section, SpecializationBranch

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['identification_number', 'role', 'is_active', 'date_joined']
        read_only_fields = ['is_active', 'date_joined']

class StudentRegistrationSerializer(serializers.ModelSerializer):
    # Basic user fields
    identification_number = serializers.CharField(max_length=15, source='user.identification_number')
    password = serializers.CharField(max_length=128, write_only=True, source='user.password')
    
    # Section field with queryset for dropdown
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['user']
    
    def create(self, validated_data):
        identification_number = validated_data.pop('identification_number')
        password = validated_data.pop('password')
        user_data = {'identification_number': identification_number, 'password': password}
        # Create user with student role
        user = User.objects.create_user(
            id_number=user_data['identification_number'], 
            password=user_data['password'],
            role='student'
        )
        # Create student profile
        student = Student.objects.create(user=user, **validated_data)
        return student

class TeacherRegistrationSerializer(serializers.ModelSerializer):
    # Basic user fields
    identification_number = serializers.CharField(max_length=15, source='user.identification_number')
    password = serializers.CharField(max_length=128, write_only=True, source='user.password')
    
    # SpecializationBranch field with queryset for dropdown
    specialization_branch = serializers.PrimaryKeyRelatedField(queryset=SpecializationBranch.objects.all())
    
    class Meta:
        model = Teacher
        fields = '__all__'
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # Create user with teacher role
        user = User.objects.create_user(
            id_number=user_data['identification_number'], 
            password=user_data['password'],
            role='teacher'
        )
        # Create teacher profile
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

class StudentProfileSerializer(serializers.ModelSerializer):
    identification_number = serializers.CharField(source='user.identification_number', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    specialization_branch_name = serializers.CharField(source='section.specialization_branch.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['identification_number', 'role', 'first_name', 'last_name', 
                  'phone_number', 'batch', 'section', 'section_name', 'specialization_branch_name']
        read_only_fields = ['identification_number', 'role', 'section_name', 'specialization_branch_name']

class TeacherProfileSerializer(serializers.ModelSerializer):
    identification_number = serializers.CharField(source='user.identification_number', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    specialization_name = serializers.CharField(source='specialization_branch.name', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['identification_number', 'role', 'first_name', 'last_name', 
                  'phone_number', 'department', 'specialization_branch', 'specialization_name']
        read_only_fields = ['identification_number', 'role', 'specialization_name']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value