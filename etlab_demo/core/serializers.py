from rest_framework import serializers
from .models import Student

class studentSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    class Meta:
        model = Student
        fields = ['reg_number', 'name', 'semester']