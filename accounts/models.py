from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_verified_code = models.CharField(max_length=100, blank=True)
    verification_code_expiry = models.DateTimeField(null=True, blank=True)  # 验证码超时时间

    def is_verification_code_expired(self):
        return timezone.now() > self.verification_code_expiry if self.verification_code_expiry else True