from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
import uuid
import os
from datetime import datetime
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import UserProfile
from .models import TrafficViolation, MediaFile
from .utils import (
    process_input, 
    ReportManager,
)
from google.cloud import bigquery
from .mysql_utils import (
    get_traffic_violation_markers,
    get_traffic_violation_details,
    search_traffic_violations,
    get_user_records,
)


# 修改後的 search_traffic_violations_view
def search_traffic_violations_view(request):
    keyword = request.GET.get('keyword', '')
    time_range = request.GET.get('timeRange', 'all')
    from_date = request.GET.get('fromDate', '')
    to_date = request.GET.get('toDate', '')

    data = search_traffic_violations(keyword, time_range, from_date, to_date)
    return JsonResponse(data, safe=False)

# 修改後的 traffic_violation_markers_view
def traffic_violation_markers_view(request):
    data = get_traffic_violation_markers()
    return JsonResponse(data, safe=False)

# 修改後的 traffic_violation_details_view
def traffic_violation_details_view(request, traffic_violation_id):
    data = get_traffic_violation_details(traffic_violation_id)
    return JsonResponse(data)

def home(request):
    context = {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'reports/home.html', context)

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
            # Create a new TrafficViolation instance using the validated form data
            traffic_violation = TrafficViolation(
                license_plate=form.cleaned_data['license_plate'],
                date=form.cleaned_data['date'],
                time=form.cleaned_data['time'],
                violation=form.cleaned_data['violation'],
                status=form.cleaned_data['status'],
                location=process_input(form.cleaned_data['location']),
                officer=request.user.username if form.cleaned_data['officer'] else None,  # 这里假设 officer 字段是文本类型
                username=request.user.username
            )
            traffic_violation.save()

            # Handle file uploads
            for file in request.FILES.getlist('media'):
                # Create and save MediaFile instance
                MediaFile.objects.create(
                    traffic_violation=traffic_violation,
                    file=file  # 直接传递文件对象
                )

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')
    else:
        form = ReportForm()

    return render(request, 'reports/dashboard.html', {'form': form})
