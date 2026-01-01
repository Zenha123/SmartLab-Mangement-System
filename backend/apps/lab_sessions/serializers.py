from rest_framework import serializers
from .models import LabSession


class LabSessionSerializer(serializers.ModelSerializer):
    """Serializer for Lab Session"""
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    batch_name = serializers.CharField(source='batch.__str__', read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LabSession
        fields = [
            'id', 'faculty', 'faculty_name', 'batch', 'batch_name',
            'session_type', 'status', 'start_time', 'end_time', 'duration_minutes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'faculty', 'created_at', 'updated_at']
