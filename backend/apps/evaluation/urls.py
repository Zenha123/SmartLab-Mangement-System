from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'viva', views.VivaRecordViewSet, basename='viva')
router.register(r'exams', views.ExamSessionViewSet, basename='exam')
router.register(r'exam-results', views.ExamResultViewSet, basename='exam-result')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'submissions', views.TaskSubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/attendance/', views.attendance_report, name='attendance-report'),
    path('reports/viva/', views.viva_report, name='viva-report'),
    path('reports/submissions/', views.submission_report, name='submission-report'),
]
