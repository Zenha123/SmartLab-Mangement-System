from rest_framework import serializers
from .models import Student, Faculty, Timetable

class studentSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    class Meta:
        model = Student
        fields = ['reg_number', 'name', 'semester']


class facultySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Faculty
        fields = ['faculty_id', 'name', 'email', 'role']


class timetableSyncSerializer(serializers.ModelSerializer):
    semester_number = serializers.IntegerField(source="semester.number", read_only=True)
    semester_name = serializers.CharField(source="semester.semester_name", read_only=True)
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)
    faculty_id = serializers.CharField(source="faculty.faculty_id", read_only=True)

    class Meta:
        model = Timetable
        fields = ['semester_number', 'semester_name', 'day_of_week', 'hour_slot', 'subject_name', 'faculty_id']
