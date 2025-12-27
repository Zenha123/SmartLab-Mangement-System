from django.db import models
from django.utils import timezone


class LabSession(models.Model):
    """Lab session created by faculty"""
    
    SESSION_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('viva', 'Viva'),
        ('exam', 'Exam'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('paused', 'Paused'),
    ]
    
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='lab_sessions')
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='lab_sessions')
    
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default='regular')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_sessions'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.session_type.title()} - {self.batch} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def end_session(self):
        """End the lab session"""
        self.status = 'ended'
        self.end_time = timezone.now()
        self.save(update_fields=['status', 'end_time'])
    
    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        else:
            delta = timezone.now() - self.start_time
            return int(delta.total_seconds() / 60)
