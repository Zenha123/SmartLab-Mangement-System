from django.contrib import admin
from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model"""
    
    list_display = ('student_id', 'name', 'batch', 'status', 'current_mode', 'last_seen', 'created_at')
    list_filter = ('status', 'current_mode', 'batch', 'created_at')
    search_fields = ('student_id', 'name', 'email')
    ordering = ('student_id',)
    readonly_fields = ('created_at', 'updated_at', 'last_seen')
    
    fieldsets = (
        ('Basic Information', {'fields': ('student_id', 'name', 'email', 'batch')}),
        ('Status', {'fields': ('status', 'current_mode', 'last_seen')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model"""
    
    list_display = ('student', 'session', 'status', 'login_time', 'logout_time', 'duration_display', 'created_at')
    list_filter = ('status', 'session__batch', 'created_at', 'login_time')
    search_fields = ('student__name', 'student__student_id', 'session__batch__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'duration_display')
    
    fieldsets = (
        (None, {'fields': ('student', 'session', 'status')}),
        ('Time Details', {'fields': ('login_time', 'logout_time', 'duration_display')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def duration_display(self, obj):
        """Display duration in minutes"""
        duration = obj.get_duration()
        if duration:
            return f"{duration} minutes"
        return "N/A"
    duration_display.short_description = 'Duration'
