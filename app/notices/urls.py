from rest_framework.routers import DefaultRouter
from .views import NoticeViewSet
from django.urls import path,include

router=DefaultRouter()

router.register('notices',NoticeViewSet)

url_patterns=[
    path('notices',include(router.urls))
]