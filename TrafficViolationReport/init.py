from __future__ import absolute_import, unicode_literals

# 这将确保在 Django 启动时 Celery 应用程序总是被导入
from .celery import app as celery_app

__all__ = ('celery_app',)
