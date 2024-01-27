from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'email_verified', 'email_verified_code', 'verification_code_expiry']

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ['provider', 'uid', 'last_login', 'date_joined', 'extra_data']

class UserProfileWithSocialSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    social_accounts = SocialAccountSerializer(many=True, read_only=True)  # 添加一个新的字段 social_accounts

    class Meta:
        model = UserProfile
        fields = ['user', 'email_verified', 'email_verified_code', 'verification_code_expiry', 'social_accounts']
