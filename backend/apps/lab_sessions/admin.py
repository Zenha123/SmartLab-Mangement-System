from django.contrib import admin
from .models import LabSession


@admin.register(LabSession)
class LabSessionAdmin(admin.ModelAdmin):
    """Admin configuration for Lab Session model"""
    
    list_display = ('id', 'batch', 'faculty', 'session_type', 'status', 'start_time', 'end_time', 'duration_display')
    list_filter = ('status', 'session_type', 'batch', 'start_time')
    search_fields = ('batch__name', 'faculty__name', 'faculty__faculty_id')
    ordering = ('-start_time',)
    readonly_fields = ('created_at', 'updated_at', 'duration_display')
    
    fieldsets = (
        ('Session Details', {'fields': ('batch', 'faculty', 'session_type', 'status')}),
        ('Time Information', {'fields': ('start_time', 'end_time', 'duration_display')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def duration_display(self, obj):
        """Display session duration in minutes"""
        try:
            duration = obj.duration_minutes
            if duration:
                return f"{duration} minutes"
        except Exception:
            pass
        return "In Progress" if obj.status == 'active' else "N/A"
    duration_display.short_description = 'Duration'
    
    actions = ['end_selected_sessions']
    
    def end_selected_sessions(self, request, queryset):
        """Admin action to end multiple sessions"""
        count = 0
        for session in queryset.filter(status='active'):
            session.end_session()
            count += 1
        self.message_user(request, f"{count} session(s) ended successfully.")
    end_selected_sessions.short_description = "End selected active sessions"
