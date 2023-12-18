from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrafficViolationReport.settings')

app = Celery('TrafficViolationReport')

# 使用 Django 的设置文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现项目中的任务
app.autodiscover_tasks()
