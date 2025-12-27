from django.contrib import admin
from .models import Student, Timetable, Faculty, Subject, Semester,AttendanceSession,AttendanceRecord

admin.site.register(Student)
admin.site.register(Timetable)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(Semester)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
