from django.urls import path
from .views import attendance_week_view, faculty_dashboard, login_view, mark_attendance, semester_list, semester_detail

urlpatterns = [
    path('', login_view, name='login'),
    path('etlab-admin/semesters/', semester_list, name='semester_list'),
    path('etlab-admin/semester/<int:sem>/', semester_detail, name='semester_detail'),
    path('faculty/dashboard/', faculty_dashboard, name='faculty_dashboard'),
    path('faculty/attendance/<int:subject_id>/', attendance_week_view, name='attendance_week'),  # Placeholder
    path('faculty/mark-attendance/', mark_attendance, name='mark_attendance'),  # Placeholder
]
