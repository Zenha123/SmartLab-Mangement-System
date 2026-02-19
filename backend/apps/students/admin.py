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
    
    def save_model(self, request, obj, form, change):
        """Auto-create User for the student if not selected"""
        if not obj.pk and not getattr(obj, 'user', None):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Use student_id as the unique identifier (mapped to faculty_id in User model)
            user_id = obj.student_id
            
            # Check if user exists
            existing_user = User.objects.filter(faculty_id=user_id).first()
            if existing_user:
                obj.user = existing_user
            else:
                # Create new user
                # Ensure email exists or create dummy
                email = obj.email if obj.email else f"{user_id}@smartlab.local"
                
                obj.user = User.objects.create_user(
                    faculty_id=user_id,
                    email=email,
                    password=user_id,  # Default password is the ID
                    name=obj.name,
                    is_active=True
                )
                self.message_user(request, f"Created new User account for {user_id} with password '{user_id}'")
                
        super().save_model(request, obj, form, change)

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