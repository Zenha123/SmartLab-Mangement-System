from django.contrib import admin
from .models import Semester, Batch, PCMapping


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    """Admin configuration for Semester model"""
    
    list_display = ('name', 'number', 'is_active', 'created_at')
    list_filter = ('is_active', 'number')
    search_fields = ('name',)
    ordering = ('number',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('name', 'number', 'is_active')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    """Admin configuration for Batch model"""
    
    list_display = ('name', 'semester', 'year', 'total_students', 'is_active', 'created_at')
    list_filter = ('is_active', 'semester', 'year')
    search_fields = ('name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('semester', 'name', 'year')}),
        ('Details', {'fields': ('total_students', 'is_active')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(PCMapping)
class PCMappingAdmin(admin.ModelAdmin):
    """Admin configuration for PC Mapping model"""
    
    list_display = ('pc_id', 'student', 'batch', 'is_active', 'created_at')
    list_filter = ('is_active', 'batch', 'created_at')
    search_fields = ('pc_id', 'student__name', 'student__student_id')
    ordering = ('pc_id',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('pc_id', 'student', 'batch')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
