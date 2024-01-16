from rest_framework import serializers
from .models import TrafficViolation, MediaFile

class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = '__all__'

class TrafficViolationSerializer(serializers.ModelSerializer):
    media_files = MediaFileSerializer(many=True)  # 嵌套序列化媒體資訊

    class Meta:
        model = TrafficViolation
        fields = '__all__'
