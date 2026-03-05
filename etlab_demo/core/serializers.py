from rest_framework import serializers
from .models import Student, Faculty

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
