from django.db import models
from django.contrib.auth.models import User


# ---------------- SEMESTER ----------------
class Semester(models.Model):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty_name = models.CharField(max_length=100)

    def __str__(self):
        return self.faculty_name


# Student belongs to a semester
class Student(models.Model):
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.roll_no


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