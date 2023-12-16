from django.urls import path
from . import views

app_name = 'traffic_data'

urlpatterns = [
    # path('', views.home, name='home'),
    path('traffic-violation-details/<str:traffic_violation_id>/', views.traffic_violation_details_view, name='traffic-violation-details'),
    path('search-traffic-violations/', views.search_traffic_violations_view, name='search-traffic-violations'),
    path('traffic-violation-markers/', views.traffic_violation_markers_view, name='traffic-violation-markers'),
    
    # path('', some_app_views.home_view, name='home'),  # Add this line for the root URL
]