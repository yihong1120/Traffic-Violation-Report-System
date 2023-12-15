from django.urls import path
from . import views

app_name = 'traffic_data'

urlpatterns = [
    path('', views.home, name='home'),
    path('search-traffic-violations/', views.search_traffic_violations, name='search_traffic_violations'),
    path('traffic-violation-markers/', views.get_traffic_violation_markers, name='traffic-violation-markers'),
    path('', views.home, name='home'),  # 假设 home 视图在 traffic_data 应用程序中
]