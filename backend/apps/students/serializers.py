from rest_framework import serializers
from .models import Student, Attendance


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student with real-time status"""
    pc_id = serializers.CharField(read_only=True)
    batch_name = serializers.CharField(source='batch.__str__', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'name', 'email', 'batch', 'batch_name',
            'status', 'current_mode', 'last_seen', 'pc_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'pc_id', 'created_at', 'updated_at']


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance records"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    session_info = serializers.CharField(source='session.__str__', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'student_id', 'session', 'session_info',
            'login_time', 'logout_time', 'duration_minutes', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
