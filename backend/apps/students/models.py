from django.db import models
from django.utils import timezone
from django.conf import settings



class Student(models.Model):
    """Student profile and current status"""
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    MODE_CHOICES = [
        ('normal', 'Normal'),
        ('locked', 'Locked'),
        ('viva', 'Viva'),
        ('exam', 'Exam'),
    ]

    user= models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=False, blank=False,
    )
    
    student_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='students')
    
    # Real-time status tracking
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    current_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='normal')
    last_seen = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"
    
    def mark_online(self):
        """Mark student as online and update last_seen"""
        self.status = 'online'
        self.last_seen = timezone.now()
        self.save(update_fields=['status', 'last_seen'])
    
    def mark_offline(self):
        """Mark student as offline"""
        self.status = 'offline'
        self.last_seen = timezone.now()
        self.save(update_fields=['status', 'last_seen'])
    
    def set_mode(self, mode):
        """Change student's current mode"""
        if mode in dict(self.MODE_CHOICES):
            self.current_mode = mode
            self.save(update_fields=['current_mode'])
    
    @property
    def pc_id(self):
        """Get the PC ID assigned to this student"""
        try:
            return self.pc_mapping.pc_id
        except:
            return None


class Attendance(models.Model):
    """Tracks student attendance during lab sessions"""
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    session = models.ForeignKey('lab_sessions.LabSession', on_delete=models.CASCADE, related_name='attendance_records')
    
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance'
        ordering = ['-created_at']
        unique_together = ['student', 'session']
    
    def __str__(self):
        return f"{self.student.name} - {self.session} - {self.status}"
    
    def calculate_duration(self):
        """Calculate duration in minutes if both login and logout times exist"""
        if self.login_time and self.logout_time:
            delta = self.logout_time - self.login_time
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.save(update_fields=['duration_minutes'])

