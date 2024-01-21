from django.urls import path
from . import views, api_views

app_name = 'reports'

urlpatterns = [
    # WEB path
    # path('edit-report/', views.edit_report, name='edit_report'),
    path('upload/', views.dashboard, name='file_upload'),
    # path('dashboard/', views.dashboard, name='dashboard'),

    # API path
    path('api/create-report/', api_views.create_report_api, name='api_create_report'),
    path('api/traffic-violations-list/', api_views.traffic_violation_list_api, name='api_traffic_violations_list'),
    path('api/traffic-violations-detail/', api_views.traffic_violation_detail_api, name='api_traffic_violation_detail'),
    path('api/update-report/<uuid:violation_id>/', api_views.update_report_api, name='api_update_report'),
]