from rest_framework.decorators import api_view
from rest_framework.response import Response
from reports.models import TrafficViolation
from .serializers import TrafficViolationSerializer, TrafficViolationMarkerSerializer
from utils.mysql_utils import (
    get_traffic_violation_markers,
    get_traffic_violation_details,
    search_traffic_violations,
)

@api_view(['GET'])
def search_traffic_violations_api(request):
    keyword = request.GET.get('keyword', '')
    time_range = request.GET.get('timeRange', 'all')
    from_date = request.GET.get('fromDate', '')
    to_date = request.GET.get('toDate', '')

    violations = search_traffic_violations(keyword, time_range, from_date, to_date)
    serializer = TrafficViolationMarkerSerializer(violations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def traffic_violation_markers_api(request):
    markers = get_traffic_violation_markers(request)
    serializer = TrafficViolationMarkerSerializer(markers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def traffic_violation_details_api(request, traffic_violation_id):
    try:
        # 使用 valid_uuid 获取 TrafficViolation 对象
        violation = TrafficViolation.objects.get(traffic_violation_id=traffic_violation_id)
        serializer = TrafficViolationSerializer(violation)

        return Response(serializer.data)
    except TrafficViolation.DoesNotExist:
        # 如果 TrafficViolation 对象不存在，返回一个 404 错误响应
        return Response(status=404)