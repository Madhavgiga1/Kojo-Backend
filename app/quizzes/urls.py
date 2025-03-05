from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet, QuestionView, QuestionOptionView,
    QuizQuestionAnswerView, QuizSubmissionViewSet
)

router = DefaultRouter()

app_name = 'quizzes'
router.register('quizzes', QuizViewSet, basename='quiz')
router.register('submitted-quizzes', QuizSubmissionViewSet, basename='submission-answer')

urlpatterns = [
    path('', include(router.urls)),
    path('answers/', QuizQuestionAnswerView.as_view(), name='student-answer'),
    path('questions/', QuestionView.as_view(), name='question'),
    path('options/', QuestionOptionView.as_view(), name='create-option'),
]