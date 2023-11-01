from django.db import models

# Create your models here.
class TrafficViolation(models.Model):
    license_plate = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    officer = models.CharField(max_length=255, blank=True, null=True)
    media = models.FileField(upload_to='media/')
