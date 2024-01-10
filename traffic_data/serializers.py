from rest_framework import serializers
from reports.models import TrafficViolation

class TrafficViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficViolation
        fields = '__all__'

class TrafficViolationMarkerSerializer(serializers.Serializer):
    traffic_violation_id = serializers.UUIDField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()