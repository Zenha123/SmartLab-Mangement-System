from rest_framework import serializers
from .models import Semester, Batch, PCMapping


class SemesterSerializer(serializers.ModelSerializer):
    """Serializer for Semester"""
    
    class Meta:
        model = Semester
        fields = ['id', 'name', 'number', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class BatchSerializer(serializers.ModelSerializer):
    """Serializer for Batch"""
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    
    class Meta:
        model = Batch
        fields = ['id', 'semester', 'semester_name', 'name', 'year', 'total_students', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class PCMappingSerializer(serializers.ModelSerializer):
    """Serializer for PC Mapping"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    batch_name = serializers.CharField(source='batch.__str__', read_only=True)
    
    class Meta:
        model = PCMapping
        fields = ['id', 'pc_id', 'student', 'student_name', 'batch', 'batch_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
