from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['faculty_id', 'name', 'email', 'is_active', 'is_staff', 'last_login']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['faculty_id', 'name', 'email']
    ordering = ['faculty_id']
    
    fieldsets = (
        (None, {'fields': ('faculty_id', 'email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('faculty_id', 'email', 'name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login']
