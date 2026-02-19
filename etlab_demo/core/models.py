from django.db import models
from django.contrib.auth.models import User


# ---------------- SEMESTER ----------------
class Semester(models.Model):
    number = models.IntegerField(unique=True)
    semester_name = models.CharField(max_length=50)  # e.g. "Semester 3"

    def __str__(self):
        return self.semester_name
    

# ---------------- SUBJECT ----------------
class Subject(models.Model):
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subject_name
    


# Faculty profile (created via Django admin)
class Faculty(models.Model):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("FACULTY", "Faculty"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


    def is_admin(self):
        return self.role == "ADMIN"

    def is_faculty(self):
        return self.role == "FACULTY"

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ---------------- STUDENT ----------------
# Student belongs to a semester
class Student(models.Model):
    reg_number = models.CharField(
        max_length=20,
        primary_key=True
    )
    name = models.CharField(max_length=100)
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.reg_number} - {self.name}"



# Timetable entry
# ---------------- TIMETABLE ----------------
class Timetable(models.Model):
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    hour_slot = models.IntegerField()  # 1 to 6

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('semester', 'day_of_week', 'hour_slot')

    def __str__(self):
        return f"{self.semester} {self.day_of_week} H{self.hour_slot}"
    
# ---------------- ATTENDANCE SESSION ----------------
class AttendanceSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    date = models.DateField()
    period = models.IntegerField()
    is_suspended = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            'date',
            'semester',
            'subject',
            'faculty',
            'period'
        )

    def __str__(self):
        return f"{self.subject} | {self.date} | P{self.period}"


# ---------------- ATTENDANCE RECORD ----------------
class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)

# ---------------- MARKS ----------------
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    internal_marks = models.IntegerField(default=0)
    assignment_marks = models.IntegerField(default=0)
    lab_marks = models.IntegerField(default=0)

    total_marks = models.IntegerField(default=0)

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'subject', 'semester')

    def save(self, *args, **kwargs):
        self.total_marks = (
            self.internal_marks +
            self.assignment_marks +
            self.lab_marks
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject}"
