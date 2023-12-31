from django.urls import path
from . import views

app_name = 'traffic_data'

urlpatterns = [
    path('traffic-violation-details/<str:traffic_violation_id>/', views.traffic_violation_details_view, name='traffic-violation-details'),
    path('search-traffic-violations/', views.search_traffic_violations_view, name='search-traffic-violations'),
    path('traffic-violation-markers/', views.traffic_violation_markers_view, name='traffic-violation-markers'),
    
    # API path
    path('api/search-traffic-violations/', views.search_traffic_violations_view, name='api_search_traffic_violations'),
    path('api/traffic-violation-markers/', views.traffic_violation_markers_view, name='api_traffic_violation_markers'),
    path('api/traffic-violation-details/<str:traffic_violation_id>/', views.traffic_violation_details_view, name='api_traffic_violation_details'),
]