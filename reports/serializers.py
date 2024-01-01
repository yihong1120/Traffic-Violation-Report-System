from rest_framework import serializers
from .models import TrafficViolation, MediaFile

class TrafficViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficViolation
        fields = '__all__'

class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = '__all__'
