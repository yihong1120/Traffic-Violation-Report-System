from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('search-traffic-violations/', views.search_traffic_violations, name='search_traffic_violations'),
    path('traffic-violation-markers/', views.get_traffic_violation_markers, name='traffic-violation-markers'),
    path('traffic-violation-details/<str:traffic_violation_id>/', views.get_traffic_violation_details, name='traffic-violation-details'),
    path('edit-report/', views.edit_report, name='edit_report'),
    path('upload/', views.dashboard, name='file_upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),  # 假设 home 视图在 reports 应用程序中
]