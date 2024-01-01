from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # path('edit-report/', views.edit_report, name='edit_report'),
    path('upload/', views.dashboard, name='file_upload'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('api/traffic-violations/', views.traffic_violation_list, name='traffic_violation_list'),
]