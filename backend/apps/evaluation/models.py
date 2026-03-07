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
    """Lab Exam session — standalone, created directly by faculty"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200, default='Lab Exam')
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='exam_sessions')
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='exam_sessions')
    duration_minutes = models.IntegerField(default=120)
    subject_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} — {self.batch.name} ({self.status})"


class ExamQuestion(models.Model):
    """Question bank per exam session"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=300)
    description = models.TextField()
    marks = models.IntegerField(default=10)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exam_questions'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Q: {self.title[:50]} [{self.session.title}]"


class StudentExam(models.Model):
    """Per-student exam record: assigned questions, submission, evaluation"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('evaluated', 'Evaluated'),
    ]
    
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='student_exams')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='student_exams')
    assigned_questions = models.ManyToManyField(ExamQuestion, blank=True, related_name='student_exams')
    
    submission_file = models.FileField(upload_to='exam_submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    marks = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_exams'
        ordering = ['-created_at']
        unique_together = ['session', 'student']
    
    def __str__(self):
        return f"{self.student.name} — {self.session.title} ({self.status})"


class Task(models.Model):
    """Task/assignment distributed to batch"""
    
    batch = models.ForeignKey('core.Batch', on_delete=models.CASCADE, related_name='tasks')
    faculty = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='tasks')
    
    title = models.CharField(max_length=200)
    subject_name = models.CharField(max_length=100, blank=True, null=True)
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
