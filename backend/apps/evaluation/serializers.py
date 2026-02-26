from rest_framework import serializers
from .models import VivaRecord, VivaSession, ExamSession, ExamQuestion, StudentExam, Task, TaskSubmission


class VivaSessionSerializer(serializers.ModelSerializer):
    """Serializer for Viva Session"""
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    # Explicit field types to prevent "Expected a date, but got a datetime" errors
    date = serializers.DateField(required=False, default=None)  # Auto-set in model if blank
    start_time = serializers.DateTimeField(
        required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601']
    )
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    
    class Meta:
        model = VivaSession
        fields = [
            'id', 'faculty', 'faculty_name', 'batch', 'batch_name', 'subject',
            'viva_type', 'status', 'date', 'platform_name', 'join_code',
            'join_link', 'start_time', 'instructions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'faculty', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Set today's date if not provided"""
        from django.utils import timezone
        if not attrs.get('date'):
            attrs['date'] = timezone.now().date()
        return attrs


class VivaRecordSerializer(serializers.ModelSerializer):
    """Serializer for Viva Record"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll = serializers.CharField(source='student.register_number', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    conducted_at = serializers.DateTimeField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = VivaRecord
        fields = [
            'id', 'student', 'student_name', 'student_roll',
            'viva_session', 'session', 'faculty', 'faculty_name',
            'marks', 'notes', 'is_published', 'status', 'conducted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'faculty', 'created_at', 'updated_at']
    
    def validate_marks(self, value):
        """Validate marks are between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Marks must be between 0 and 100")
        return value


class ExamSessionSerializer(serializers.ModelSerializer):
    """Serializer for the new standalone ExamSession"""
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    question_count = serializers.IntegerField(source='questions.count', read_only=True)
    submission_count = serializers.IntegerField(source='student_exams.count', read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    class Meta:
        model = ExamSession
        fields = [
            'id', 'title', 'batch', 'batch_name', 'faculty', 'faculty_name',
            'duration_minutes', 'status', 'question_count', 'submission_count', 'created_at',
        ]
        read_only_fields = ['id', 'faculty', 'created_at']


class ExamQuestionSerializer(serializers.ModelSerializer):
    """Serializer for ExamQuestion"""
    class Meta:
        model = ExamQuestion
        fields = ['id', 'session', 'title', 'description', 'marks', 'difficulty', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentExamSerializer(serializers.ModelSerializer):
    """Serializer for StudentExam (faculty view — includes file URL)"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll = serializers.CharField(source='student.register_number', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    assigned_questions = ExamQuestionSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    submitted_at = serializers.DateTimeField(read_only=True, format='iso-8601', allow_null=True)

    class Meta:
        model = StudentExam
        fields = [
            'id', 'session', 'session_title', 'student', 'student_name', 'student_roll',
            'assigned_questions', 'submission_file', 'file_url', 'submitted_at',
            'marks', 'feedback', 'status', 'is_published', 'created_at',
        ]
        read_only_fields = ['id', 'student', 'session', 'submitted_at', 'created_at']

    def get_file_url(self, obj):
        if obj.submission_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.submission_file.url)
            return obj.submission_file.url
        return None




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
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'faculty', 'created_at', 'updated_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class TaskSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Task Submission"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    file_path = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskSubmission
        fields = [
            'id', 'task', 'task_title', 'student', 'student_name',
            'file_path', 'submission_file', 'submitted_at',
            'marks', 'feedback', 'is_published', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'created_at', 'updated_at']

    def get_file_path(self, obj):
        """Return relative path for backward compatibility"""
        if obj.submission_file:
            return obj.submission_file.name
        return obj.file_path
    
    def validate_marks(self, value):
        """Validate marks are between 0 and 100"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Marks must be between 0 and 100")
        return value
