from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'viva-sessions', views.VivaSessionViewSet, basename='viva-session')
router.register(r'viva', views.VivaRecordViewSet, basename='viva')
router.register(r'exam-sessions', views.ExamSessionViewSet, basename='exam-session')
router.register(r'exam-questions', views.ExamQuestionViewSet, basename='exam-question')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'submissions', views.TaskSubmissionViewSet, basename='submission')

urlpatterns = [
    # Viva custom endpoints
    path('viva-results/', views.VivaResultView.as_view(), name='viva-results'),
    path('live-viva/', views.LiveVivaView.as_view(), name='live-viva'),

    # Exam custom endpoints
    path('exam-start/', views.ExamStartView.as_view(), name='exam-start'),
    path('exam-end/', views.ExamEndView.as_view(), name='exam-end'),
    path('exam-submissions/', views.ExamSubmissionsView.as_view(), name='exam-submissions'),
    path('exam-evaluate/', views.ExamEvaluateView.as_view(), name='exam-evaluate'),

    # Student exam endpoints
    path('my-exam/', views.MyExamView.as_view(), name='my-exam'),
    path('submit-exam/', views.SubmitExamView.as_view(), name='submit-exam'),

    # Router-based endpoints
    path('', include(router.urls)),

    # Reports
    path('reports/attendance/', views.attendance_report, name='attendance-report'),
    path('reports/viva/', views.viva_report, name='viva-report'),
    path('reports/submissions/', views.submission_report, name='submission-report'),
]
