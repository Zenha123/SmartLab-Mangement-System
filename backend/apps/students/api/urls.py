from django.urls import path, include
from .auth_views import StudentLoginView

urlpatterns = [
    path('student/login/', StudentLoginView.as_view(), name='student-login'),
]