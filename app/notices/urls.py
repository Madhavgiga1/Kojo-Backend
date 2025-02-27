from rest_framework.routers import DefaultRouter
from .views import NoticeViewSet
from django.urls import path,include

router=DefaultRouter()

router.register('',NoticeViewSet)
app_name='notice'

urlpatterns=[
    path('',include(router.urls))
]