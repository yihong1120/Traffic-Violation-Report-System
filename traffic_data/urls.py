from django.urls import path
from . import views, api_views

app_name = 'traffic_data'

urlpatterns = [
    # WEB path
    path('traffic-violation-details/<str:traffic_violation_id>/', views.traffic_violation_details_view, name='traffic-violation-details'),
    path('search-traffic-violations/', views.search_traffic_violations_view, name='search-traffic-violations'),
    path('traffic-violation-markers/', views.traffic_violation_markers_view, name='traffic-violation-markers'),
    
    # API path
    path('api/search-traffic-violations/', api_views.search_traffic_violations_api, name='api_search_traffic_violations'),
    path('api/traffic-violation-markers/', api_views.traffic_violation_markers_api, name='api_traffic_violation_markers'),
    path('api/traffic-violation-details/<uuid:traffic_violation_id>/', api_views.traffic_violation_details_api, name='api_traffic_violation_details'),
]