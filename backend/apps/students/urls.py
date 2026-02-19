from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api.logout import StudentLogoutAPIView

router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('api/student/login/', views.StudentLoginView.as_view(), name='student-login'),
    path("logout/", StudentLogoutAPIView.as_view(), name="student-logout"),
    path("student/me/", views.studentMeView.as_view(), name="student-me"),
    #path("student/online_count/", views.online_students_count, name="online-students-count"),
]
