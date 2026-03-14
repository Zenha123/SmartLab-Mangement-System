from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ControlViewSet

router = DefaultRouter()
router.register(r'control', ControlViewSet, basename='control')

urlpatterns = [
    path('', include(router.urls)),
]
