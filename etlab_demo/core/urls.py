from django.urls import path
from .views import (
    attendance_week_view,
    faculty_dashboard,
    login_view,
    mark_attendance,
    semester_list,
    semester_detail,
    logout_view,
    mark_marks,
    faculty_report,
    sync_faculty_now,
    sync_students_now,
    sync_timetable_now,
    upload_faculty_csv,
    upload_students_csv,
)
from .api_views import student_list, faculty_list, timetable_list, attendance_sync

urlpatterns = [
    path('', login_view, name='login'),
    path('etlab-admin/semesters/', semester_list, name='semester_list'),
    path('etlab-admin/semester/<int:sem>/', semester_detail, name='semester_detail'),
    path('etlab-admin/semester/<int:sem>/upload-students-csv/', upload_students_csv, name='upload_students_csv'),
    path('etlab-admin/sync-faculty-now/', sync_faculty_now, name='sync_faculty_now'),
    path('etlab-admin/sync-students-now/', sync_students_now, name='sync_students_now'),
    path('etlab-admin/sync-timetable-now/', sync_timetable_now, name='sync_timetable_now'),
    path('etlab-admin/upload-faculty-csv/', upload_faculty_csv, name='upload_faculty_csv'),
    path('faculty/dashboard/', faculty_dashboard, name='faculty_dashboard'),
    path('faculty/attendance/<int:subject_id>/', attendance_week_view, name='attendance_week'),  # Placeholder
    path('faculty/mark-attendance/', mark_attendance, name='mark_attendance'),  # Placeholder
    path('api/students/', student_list, name='api_students'),  # New API endpoint
    path('api/faculty/', faculty_list, name='api_faculty'),
    path('api/timetable/', timetable_list, name='api_timetable'),
    path('api/attendance/sync/', attendance_sync, name='api_attendance_sync'),
    path('logout/', logout_view, name='logout'),  # Logout view
    path("marks/<int:subject_id>/<int:semester_id>/",mark_marks,name="mark_marks"),
    path(
    'report/<int:subject_id>/<int:semester_id>/',
    faculty_report,
    name='faculty_report'
),


]
