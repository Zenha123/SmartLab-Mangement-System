from django.contrib import admin
from .models import VivaRecord, VivaSession, ExamSession, ExamQuestion, StudentExam, Task, TaskSubmission


@admin.register(VivaRecord)
class VivaRecordAdmin(admin.ModelAdmin):
    """Admin configuration for Viva Record model"""
    list_display = ('student', 'viva_session', 'faculty', 'marks', 'status', 'is_published', 'conducted_at')
    list_filter = ('status', 'is_published', 'conducted_at')
    search_fields = ('student__name', 'faculty__name', 'notes')
    ordering = ('-conducted_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VivaSession)
class VivaSessionAdmin(admin.ModelAdmin):
    """Admin configuration for Viva Session model"""
    list_display = ('subject', 'batch', 'faculty', 'viva_type', 'status', 'date')
    list_filter = ('viva_type', 'status', 'created_at')
    search_fields = ('subject', 'batch__name', 'faculty__name')
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    """Admin configuration for new ExamSession model"""
    list_display = ('title', 'batch', 'faculty', 'duration_minutes', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'batch__name', 'faculty__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    """Admin configuration for ExamQuestion model"""
    list_display = ('title', 'session', 'marks', 'difficulty', 'created_at')
    list_filter = ('difficulty', 'session__status')
    search_fields = ('title', 'description', 'session__title')
    ordering = ('session', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    """Admin configuration for StudentExam model"""
    list_display = ('student', 'session', 'status', 'marks', 'is_published', 'submitted_at')
    list_filter = ('status', 'is_published', 'session')
    search_fields = ('student__name', 'session__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


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
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'


@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for Task Submission model"""
    list_display = ('student', 'task', 'submitted_at', 'marks', 'status', 'is_published')
    list_filter = ('task__batch', 'status', 'is_published', 'submitted_at')
    search_fields = ('student__name', 'task__title', 'feedback')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')

    fieldsets = (
        ('Submission Details', {'fields': ('task', 'student', 'submission_file')}),
        ('Evaluation', {'fields': ('marks', 'feedback', 'status', 'is_published')}),
        ('Timestamps', {'fields': ('submitted_at', 'created_at', 'updated_at')}),
    )
