from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
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
    username = request.user.username
    user_records = get_user_records(username)

    selected_record, form, media_urls = ReportManager.get_record_form_and_media(request, username)

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
