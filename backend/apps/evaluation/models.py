from django.db import models
from django.utils import timezone


class VivaRecord(models.Model):
    """Viva evaluation records"""
    
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
        ('absent', 'Absent'),
    ]
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='viva_records')
    session = models.ForeignKey('lab_sessions.LabSession', on_delete=models.CASCADE, related_name='viva_records')
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='viva_records')
    
    marks = models.IntegerField(null=True, blank=True)  # 0-100
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    
    conducted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'viva_records'
        ordering = ['-conducted_at']
        unique_together = ['student', 'session']
    
    def __str__(self):
        return f"Viva: {self.student.name} - {self.marks if self.marks else 'Pending'}"
    
    def mark_completed(self, marks, notes=''):
        """Mark viva as completed with marks"""
        self.marks = marks
        self.notes = notes
        self.status = 'completed'
        self.conducted_at = timezone.now()
        self.save()


class ExamSession(models.Model):
    """Exam session configuration and results"""
    
    lab_session = models.OneToOneField('lab_sessions.LabSession', on_delete=models.CASCADE, related_name='exam_session')
    exam_type = models.CharField(max_length=50, default='practical')
    duration_minutes = models.IntegerField(default=120)
    
    # Allowed applications during exam (stored as JSON-like text)
    allowed_apps = models.TextField(blank=True, help_text='Comma-separated list of allowed apps')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_sessions'
    
    def __str__(self):
        return f"Exam: {self.lab_session.batch} - {self.exam_type}"


class ExamResult(models.Model):
    """Individual student exam results"""
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_results')
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='results')
    
    marks = models.IntegerField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_results'
        ordering = ['-created_at']
        unique_together = ['student', 'exam_session']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam_session.exam_type} - {self.marks if self.marks else 'Pending'}"


class Task(models.Model):
    """Task/assignment distributed to batch"""
    
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='tasks')
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='tasks')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)
    auto_delete = models.BooleanField(default=False, help_text='Auto-delete submissions after deadline')
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.batch}"


class TaskSubmission(models.Model):
    """Student task submissions"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='task_submissions')
    
    file_path = models.CharField(max_length=500, blank=True)  # Path to uploaded file
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    marks = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_submissions'
        ordering = ['-submitted_at']
        unique_together = ['task', 'student']
    
    def __str__(self):
        return f"{self.student.name} - {self.task.title}"
