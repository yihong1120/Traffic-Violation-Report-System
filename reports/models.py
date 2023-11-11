from django.db import models
from django.contrib.auth.models import User

class TrafficViolation(models.Model):
    VIOLATIONS = [
        ('紅線停車', '紅線停車'),
        ('黃線臨車', '黃線臨車'),
        ('行駛人行道', '行駛人行道'),
        ('未停讓行人', '未停讓行人'),
        ('切換車道未打方向燈', '切換車道未打方向燈'),
        ('人行道騎樓停車', '人行道騎樓停車'),
        ('闖紅燈', '闖紅燈'),
        ('逼車', '逼車'),
        ('未禮讓直行車', '未禮讓直行車'),
        ('未依標線行駛', '未依標線行駛'),
        ('其他', '其他'),
    ]
    STATUS = [
        ('通過', '通過'),
        ('未通過', '未通過'),
        ('其他', '其他'),
    ]
    license_plate = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    violation = models.CharField(max_length=100, choices=VIOLATIONS)
    status = models.CharField(max_length=50, choices=STATUS)
    location = models.CharField(max_length=255)
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

class MediaFile(models.Model):
    traffic_violation = models.ForeignKey(TrafficViolation, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_verified_code = models.CharField(max_length=6, blank=True, null=True)