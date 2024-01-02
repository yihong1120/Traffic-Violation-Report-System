from rest_framework import serializers
from reports.models import TrafficViolation

class TrafficViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficViolation
        fields = '__all__'