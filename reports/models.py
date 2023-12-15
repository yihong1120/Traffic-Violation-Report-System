from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from django.utils.deconstruct import deconstructible


class TrafficViolation(models.Model):
    VIOLATIONS = [
        ('紅線停車', '紅線停車'),
        ('黃線臨車', '黃線臨車'),
        ('行駛人行道', '行駛人行道'),
        ('未停讓行人', '未停讓行人'),
        ('切換車道未打方向燈', '切換車道未打方向燈'),
        ('人行道停車', '人行道停車'),
        ('騎樓停車', '騎樓停車'),
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
    officer = models.CharField(max_length=255, blank=True, default='')
    traffic_violation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, blank=True, null=True)

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # 設定新文件名稱為 UUID
        filename = '{}.{}'.format(uuid.uuid4(), ext)
        # 返回包含新路徑的文件名稱
        return os.path.join(self.sub_path, filename)

# 在模型中使用 PathAndRename 來處理 'upload_to'
class MediaFile(models.Model):
    traffic_violation = models.ForeignKey(
        TrafficViolation, on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.FileField(upload_to = PathAndRename(''))
