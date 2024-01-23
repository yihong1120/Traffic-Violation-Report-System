from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # 在这里添加

    class Meta:
        model = UserProfile
        fields = ['user', 'email_verified', 'email_verified_code', 'verification_code_expiry']