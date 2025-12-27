from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Faculty user"""
    
    class Meta:
        model = User
        fields = ['id', 'faculty_id', 'name', 'email', 'last_login', 'created_at']
        read_only_fields = ['id', 'last_login', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for faculty registration"""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['faculty_id', 'email', 'name', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            faculty_id=validated_data['faculty_id'],
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login - accepts faculty_id or email"""
    faculty_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
