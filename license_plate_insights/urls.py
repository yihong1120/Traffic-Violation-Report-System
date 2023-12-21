from django.urls import path
from . import views

app_name = 'license_plate_insights'

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
]
