from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # path('edit-report/', views.edit_report, name='edit_report'),
    path('upload/', views.dashboard, name='file_upload'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('api/submit-traffic-violation/', views.submit_traffic_violation_api, name='submit_traffic_violation'),
    path('api/traffic-violations-list/', views.traffic_violation_list_api, name='traffic_violation_list'),
    path('api/traffic-violations-detail/', views.traffic_violation_detail_api, name='traffic_violation_detail'),
]