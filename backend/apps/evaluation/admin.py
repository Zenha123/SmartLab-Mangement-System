from django.contrib import admin
from .models import VivaRecord, ExamSession, ExamResult, Task, TaskSubmission


@admin.register(VivaRecord)
class VivaRecordAdmin(admin.ModelAdmin):
    """Admin configuration for Viva Record model"""
    
    list_display = ('student', 'session', 'faculty', 'marks', 'status', 'conducted_at', 'created_at')
    list_filter = ('status', 'session__batch', 'conducted_at', 'created_at')
    search_fields = ('student__name', 'student__student_id', 'faculty__name', 'notes')
    ordering = ('-conducted_at', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Viva Details', {'fields': ('student', 'session', 'faculty')}),
        ('Evaluation', {'fields': ('marks', 'notes', 'status')}),
        ('Timestamps', {'fields': ('conducted_at', 'created_at', 'updated_at')}),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    """Admin configuration for Exam Session model"""
    
    list_display = ('id', 'lab_session', 'exam_type', 'duration_minutes', 'created_at')
    list_filter = ('exam_type', 'created_at')
    search_fields = ('lab_session__batch__name', 'exam_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Exam Configuration', {'fields': ('lab_session', 'exam_type', 'duration_minutes')}),
        ('Settings', {'fields': ('allowed_apps',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """Admin configuration for Exam Result model"""
    
    list_display = ('student', 'exam_session', 'marks', 'duration_minutes', 'started_at', 'submitted_at')
    list_filter = ('exam_session__exam_type', 'submitted_at', 'created_at')
    search_fields = ('student__name', 'student__student_id')
    ordering = ('-submitted_at', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Result Details', {'fields': ('student', 'exam_session', 'marks')}),
        ('Time Information', {'fields': ('duration_minutes', 'started_at', 'submitted_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model"""
    
    list_display = ('title', 'batch', 'faculty', 'deadline', 'auto_delete', 'submission_count', 'created_at')
    list_filter = ('batch', 'auto_delete', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'batch__name', 'faculty__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'submission_count')
    
    fieldsets = (
        ('Task Information', {'fields': ('batch', 'faculty', 'title', 'description')}),
        ('Settings', {'fields': ('deadline', 'auto_delete')}),
        ('Statistics', {'fields': ('submission_count',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def submission_count(self, obj):
        """Display number of submissions"""
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for Task Submission model"""
    
    list_display = ('student', 'task', 'submitted_at', 'marks', 'file_path_display')
    list_filter = ('task__batch', 'submitted_at', 'created_at')
    search_fields = ('student__name', 'student__student_id', 'task__title', 'feedback')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Submission Details', {'fields': ('task', 'student', 'file_path')}),
        ('Evaluation', {'fields': ('marks', 'feedback')}),
        ('Timestamps', {'fields': ('submitted_at', 'created_at', 'updated_at')}),
    )
    
    def file_path_display(self, obj):
        """Display shortened file path"""
        if obj.file_path:
            return obj.file_path[:50] + '...' if len(obj.file_path) > 50 else obj.file_path
        return "No file"
    file_path_display.short_description = 'File'
