from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth_views import StudentLoginView
from .views import StudentTaskViewSet

router = DefaultRouter()
router.register(r'student/tasks', StudentTaskViewSet, basename='student-tasks')

urlpatterns = [
    path('student/login/', StudentLoginView.as_view(), name='student-login'),
    path('', include(router.urls)),
]