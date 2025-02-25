# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User, Student, Teacher, Program, SpecializationBranch, Section, 
    Subject, TeachingAssignment, Assignment, AssignmentSubmission,
    Quiz, Question, QuestionOption, QuizAttempt, StudentAnswer, Notices
)

# class UserAdmin(BaseUserAdmin):
#     model = User
#     list_display = ('identification_number', 'role', 'is_staff')
#     list_filter = ('is_staff', 'is_active', 'role')
#     fieldsets = (
#         (None, {'fields': ('identification_number', 'password')}),
#         (_('Personal info'), {'fields': ('role',)}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('date_joined',)}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('identification_number', 'role', 'password1', 'password2'),
#         }),
#     )
#     search_fields = ('identification_number',)
#     ordering = ('identification_number',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'section')
    search_fields = ('user__identification_number', 'first_name', 'last_name')
    list_filter = ('section', 'batch')

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'specialization_branch')
    search_fields = ('user__identification_number', 'first_name', 'last_name')
    list_filter = ('specialization_branch',)

# Register all models with the admin site
admin.site.register(User)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Program)
admin.site.register(SpecializationBranch)
admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(TeachingAssignment)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(QuizAttempt)
admin.site.register(StudentAnswer)
admin.site.register(Notices)