from rest_framework import serializers
from .models import VivaRecord, ExamSession, ExamResult, Task, TaskSubmission


class VivaRecordSerializer(serializers.ModelSerializer):
    """Serializer for Viva Record"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = VivaRecord
        fields = [
            'id', 'student', 'student_name', 'session', 'faculty', 'faculty_name',
            'marks', 'notes', 'status', 'conducted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_marks(self, value):
        """Validate marks are between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Marks must be between 0 and 100")
        return value


class ExamSessionSerializer(serializers.ModelSerializer):
    """Serializer for Exam Session"""
    batch_name = serializers.CharField(source='lab_session.batch.__str__', read_only=True)
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'lab_session', 'batch_name', 'exam_type', 'duration_minutes',
            'allowed_apps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamResultSerializer(serializers.ModelSerializer):
    """Serializer for Exam Result"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    exam_type = serializers.CharField(source='exam_session.exam_type', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = [
            'id', 'student', 'student_name', 'exam_session', 'exam_type',
            'marks', 'duration_minutes', 'started_at', 'submitted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_marks(self, value):
        """Validate marks are between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Marks must be between 0 and 100")
        return value


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task"""
    batch_name = serializers.CharField(source='batch.__str__', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'batch', 'batch_name', 'faculty', 'faculty_name',
            'title', 'description', 'deadline', 'auto_delete', 'submission_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class TaskSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Task Submission"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskSubmission
        fields = [
            'id', 'task', 'task_title', 'student', 'student_name',
            'file_path', 'submitted_at', 'marks', 'feedback',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'created_at', 'updated_at']
    
    def validate_marks(self, value):
        """Validate marks are between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Marks must be between 0 and 100")
        return value
