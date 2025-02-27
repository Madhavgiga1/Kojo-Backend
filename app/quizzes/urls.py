from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, StudentAnswerViewSet, QuestionViewSet, QuizSubmissionViewSet, QuizSubmissionAnswerViewSet

router = DefaultRouter()

app_name = 'quizzes'
# Add basename parameter to fix the AssertionError
router.register('', QuizViewSet, basename='quiz')
router.register('answers', StudentAnswerViewSet, basename='student-answer')
router.register('questions', QuestionViewSet, basename='question')  
router.register('submissions', QuizSubmissionViewSet, basename='quiz-submission')
router.register('submission-answers', QuizSubmissionAnswerViewSet, basename='submission-answer')

urlpatterns = [
    path('', include(router.urls))
]