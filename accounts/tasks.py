from celery import shared_task
from .models import UserProfile
from django.utils import timezone

@shared_task
def delete_expired_unverified_users():
    for profile in UserProfile.objects.filter(email_verified=False):
        if profile.is_verification_code_expired():
            profile.user.delete()
