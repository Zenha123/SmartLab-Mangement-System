from rest_framework import serializers
from .models import ControlCommand, ControlState

class ControlCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlCommand
        fields = '__all__'

class ControlStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlState
        fields = '__all__'
