from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

@login_required
def edit_report(request):
    id = request.user.id
    user_records = get_user_records(id)

    selected_record, form, media_urls = ReportManager.get_record_form_and_media(request, id)

    context = {
        'user_records': user_records,
        'selected_record': selected_record,
        'form': form,
        'media_urls': media_urls,
    }
    return render(request, 'reports/edit_report.html', context)

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # 处理输入并提取位置信息
            address, latitude, longtitude, user_input_type = process_input(form.cleaned_data['location'])

            # 创建一个新的 TrafficViolation 实例
            traffic_violation = TrafficViolation(
                license_plate=form.cleaned_data['license_plate'],
                date=form.cleaned_data['date'],
                time=form.cleaned_data['time'],
                violation=form.cleaned_data['violation'],
                status=form.cleaned_data['status'],
                address=address,
                latitude=latitude, 
                longtitude=longtitude, 
                user_input_type=user_input_type,
                officer=request.user.username if form.cleaned_data['officer'] else '',
                username=request.user.username
            )
            traffic_violation.save()

            # 处理文件上传
            for file in request.FILES.getlist('media'):
                MediaFile.objects.create(
                    traffic_violation=traffic_violation,
                    file=file
                )

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')
    else:
        form = ReportForm()

    return render(request, 'reports/dashboard.html', {'form': form})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_traffic_violation_api(request):
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
