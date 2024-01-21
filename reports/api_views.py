from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import TrafficViolationSerializer, MediaFileSerializer
from .forms import ReportForm
from .models import TrafficViolation, MediaFile
from utils.utils import (
    process_input, 
    ReportManager,
)
from utils.mysql_utils import (
    get_user_records,
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report_api(request):
    # 使用已登入的使用者來創建報告
    user = request.user
    serializer = TrafficViolationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=user)  # 將報告關聯到已登入的使用者
        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def traffic_violation_list_api(request):
    # 使用已登入的使用者id過濾違規記錄並取得標題列表
    user_id = request.user.id
    violations = TrafficViolation.objects.filter(user_id=user_id).values('id', 'title')
    return Response(violations)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def traffic_violation_detail_api(request, violation_id):
    try:
        # 获取特定交通违规的详细数据
        violation = TrafficViolation.objects.get(id=violation_id)
        
        # 验证用户是否有权访问此报告
        if violation.user != request.user:
            return Response({'detail': '您没有权限访问此报告。'}, status=403)
        
        serializer = TrafficViolationSerializer(violation)
        return Response(serializer.data)
    except TrafficViolation.DoesNotExist:
        return Response(status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_report_api(request, violation_id):
    try:
        # Get the existing TrafficViolation object
        violation = TrafficViolation.objects.get(id=violation_id)

        # Check if the user has permission to update this report
        if violation.user != request.user:
            return Response({'detail': 'You do not have permission to update this report.'}, status=status.HTTP_403_FORBIDDEN)

        # Deserialize the request data using the TrafficViolationSerializer
        serializer = TrafficViolationSerializer(instance=violation, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Save the updated report
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TrafficViolation.DoesNotExist:
        return Response({'detail': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)