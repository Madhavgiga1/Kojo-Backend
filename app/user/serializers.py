from rest_framework import serializers
from core.models import User, Teacher, Student, Section, SpecializationBranch

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['identification_number', 'role', 'is_active', 'date_joined']
        read_only_fields = ['is_active', 'date_joined']

class StudentRegistrationSerializer(serializers.ModelSerializer):
    # Basic user fields
    identification_number = serializers.CharField(max_length=15, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True, style={'input_type': 'password'})
    section_code = serializers.CharField(max_length=10, write_only=True)

    class Meta:
        model = Student
        fields = ['identification_number', 'password', 'first_name', 'last_name', 'batch', 'section_code']
        extra_kwargs = {
            'identification_number': {'write_only': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        identification_number = validated_data.pop('identification_number')
        password = validated_data.pop('password')
        section_code = validated_data.pop('section_code')

        # Check if user exists
        user = User.objects.filter(identification_number=identification_number).first()
        if not user:
            # Create new user
            user = User.objects.create_user(
                identification_number=identification_number,
                password=password,
                role='student'
            )
        elif user.role != 'student':
            raise serializers.ValidationError(
                {"identification_number": "This ID is already registered with a different role."}
            )

        # Get the section instance
        section = Section.objects.get(section_code=section_code)

        # Create student profile
        student = Student.objects.create(user=user, section=section, **validated_data)
        return student

class TeacherRegistrationSerializer(serializers.ModelSerializer):
    # Basic user fields
    identification_number = serializers.CharField(max_length=15, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True, style={'input_type': 'password'})
    specialization_branch_code = serializers.CharField(max_length=20, write_only=True)
    
    class Meta:
        model = Teacher
        fields = ['identification_number', 'password', 'first_name', 'last_name', 'department', 'specialization_branch_code']
        extra_kwargs = {
            'identification_number': {'write_only': True},
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        
        identification_number = validated_data.pop('identification_number')
        password = validated_data.pop('password')
        specialization_branch_code=validated_data.pop('specialization_branch_code')
        user=User.objects.filter(identification_number=identification_number).first()
        if user is None:
            User.objects.create_user(
                identification_number=identification_number, 
                password=password,
                role='teacher'
            )
        specialization_branch=SpecializationBranch.objects.get(specialization_branch_code=specialization_branch_code)
        teacher = Teacher.objects.create(user=user,specialization_branch=specialization_branch, **validated_data)
        return teacher

class StudentProfileSerializer(serializers.ModelSerializer):
    identification_number = serializers.CharField(source='user.identification_number', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    specialization_branch_name = serializers.CharField(source='section.specialization_branch.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['identification_number', 'role', 'first_name', 'last_name', 
                   'batch', 'section', 'section_name', 'specialization_branch_name']
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