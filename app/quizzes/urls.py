from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from views import QuizViewSet,QuestionViewSet,AnswerViewSet,QuizSubmissionViewSet,QuizSubmissionAnswerViewSet
router=DefaultRouter()

router.register(r'quizzes',QuizViewSet)
router.register(r'questions',QuestionViewSet)  
router.register(r'answers',AnswerViewSet)
router.register(r'quiz-submissions',QuizSubmissionViewSet)
router.register(r'quiz-submission-answers',QuizSubmissionAnswerViewSet)

urlpatterns = [
    path('api/',include(router.urls))
]