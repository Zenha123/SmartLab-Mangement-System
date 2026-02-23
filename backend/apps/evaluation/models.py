from django.db import models
from django.utils import timezone


class VivaSession(models.Model):
    """Configuration for a Viva session (Online or Offline)"""
    VIVA_TYPE_CHOICES = [
        ('offline', 'Offline (Face-to-Face)'),
        ('online', 'Online (Platform Based)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    ]

    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='viva_sessions')
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='viva_sessions')
    subject = models.CharField(max_length=100)
    viva_type = models.CharField(max_length=10, choices=VIVA_TYPE_CHOICES, default='offline')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    date = models.DateField(default=timezone.now)
    
    # Online Specific Fields
    platform_name = models.CharField(max_length=100, blank=True, null=True)
    join_code = models.CharField(max_length=50, blank=True, null=True)
    join_link = models.URLField(max_length=500, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'viva_sessions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.subject} - {self.get_viva_type_display()} ({self.batch.name})"


class VivaRecord(models.Model):
    """Viva evaluation records"""
    
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
        ('absent', 'Absent'),
    ]
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='viva_records')
    viva_session = models.ForeignKey(VivaSession, on_delete=models.CASCADE, related_name='records', null=True, blank=True)
    session = models.ForeignKey('lab_sessions.LabSession', on_delete=models.CASCADE, related_name='viva_records', null=True, blank=True)
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='viva_records')
    
    marks = models.IntegerField(null=True, blank=True)  # 0-100
    notes = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)  # Faculty publishes for student to see
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    
    conducted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'viva_records'
        ordering = ['-conducted_at']
        unique_together = [('student', 'viva_session')]
    
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
    
    file_path = models.CharField(max_length=500, blank=True)  # Legacy/Compatibility path
    submission_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('evaluated', 'Evaluated'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    marks = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)  # Faculty must publish to make visible to student
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_submissions'
        ordering = ['-submitted_at']
        unique_together = ['task', 'student']
    
    def __str__(self):
        return f"{self.student.name} - {self.task.title}"
