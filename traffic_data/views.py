from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from reports.models import TrafficViolation
from .serializers import TrafficViolationSerializer
from utils.mysql_utils import (
    get_traffic_violation_markers,
    get_traffic_violation_details,
    search_traffic_violations,
)
# Backup mysql to bigquery


def search_traffic_violations_view(request):
    keyword = request.GET.get('keyword', '')
    time_range = request.GET.get('timeRange', 'all')
    from_date = request.GET.get('fromDate', '')
    to_date = request.GET.get('toDate', '')

    data = search_traffic_violations(keyword, time_range, from_date, to_date)
    return JsonResponse(data, safe=False)

# 修改後的 traffic_violation_markers_view
def traffic_violation_markers_view(request):
    data = get_traffic_violation_markers(request)
    return JsonResponse(data, safe=False)

# 修改後的 traffic_violation_details_view
def traffic_violation_details_view(request, traffic_violation_id):
    data = get_traffic_violation_details(request, traffic_violation_id)
    return JsonResponse(data, safe=False)

def home(request):
    context = {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'traffic_data/home.html', context)

@api_view(['GET'])
def search_traffic_violations_view(request):
    keyword = request.GET.get('keyword', '')
    time_range = request.GET.get('timeRange', 'all')
    from_date = request.GET.get('fromDate', '')
    to_date = request.GET.get('toDate', '')

    violations = search_traffic_violations(keyword, time_range, from_date, to_date)
    serializer = TrafficViolationSerializer(violations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def traffic_violation_markers_view(request):
    markers = get_traffic_violation_markers(request)
    serializer = TrafficViolationSerializer(markers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def traffic_violation_details_view(request, traffic_violation_id):
    try:
        violation = TrafficViolation.objects.get(traffic_violation_id=traffic_violation_id)
        serializer = TrafficViolationSerializer(violation)
        return Response(serializer.data)
    except TrafficViolation.DoesNotExist:
        return Response(status=404)