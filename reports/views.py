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
from .utils import is_address, get_latitude_and_longitude, process_input, generate_random_code
from google.cloud import bigquery
from .mysql_utils import (
    get_traffic_violation_markers,
    get_traffic_violation_details,
    save_to_mysql,
    search_traffic_violations,
    get_user_records,
    get_media_records,
    update_traffic_violation,
    update_media_files,
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

def login(request, *args, **kwargs):
    # 如果用戶已登入，重定向到首頁
    if request.user.is_authenticated:
        return redirect('home')
    return LoginView.as_view()(request, *args, **kwargs)

def validate_username_email(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)

    username_error = '這個用戶名已被使用' if User.objects.filter(username=username).exists() else None
    email_error = '這個電子郵件地址已被使用' if User.objects.filter(email=email).exists() else None

    data = {
        'username_error': username_error,
        'email_error': email_error
    }
    return JsonResponse(data)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # 保存用戶模型實例

            # 為新用戶創建UserProfile實例，並生成一個隨機驗證碼
            code = generate_random_code()
            UserProfile.objects.create(user=user, email_verified_code=code)

            # 發送含有驗證碼的電子郵件
            send_mail(
                subject="驗證您的帳戶",
                message="您的驗證碼是：{code}".format(code=code),
                from_email="trafficviolationtaiwan@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            # 重定向到驗證頁面
            return redirect('verify')  # 確保你有一個名為'verify'的URL映射
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'reports/register.html', {'form': form})

def verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, '請輸入驗證碼。')
            return render(request, 'reports/verify.html')

        try:
            profile = UserProfile.objects.get(user=request.user, email_verified_code=code)
            profile.email_verified = True
            profile.email_verified_code = ''
            profile.save()
            messages.success(request, '您的帳戶已經成功驗證。')
            return redirect('login')
        except UserProfile.DoesNotExist:
            messages.error(request, '驗證碼錯誤。')
            return render(request, 'reports/verify.html')
    else:
        return render(request, 'reports/verify.html')

@login_required
def edit_report(request):
    username = request.user.username
    user_records = get_user_records(username)

    selected_record_id = request.GET.get('record_id')
    print(f"selected_record_id: {selected_record_id}")
    selected_record = None
    form = None
    media_urls = []

    if selected_record_id:
        selected_record = get_object_or_404(TrafficViolation, id=selected_record_id, username=username)
        selected_record_media = MediaFile.objects.filter(traffic_violation=selected_record)
        media_urls = [media.file.url for media in selected_record_media]

        initial_data = {
            'license_plate': selected_record.license_plate,
            'date': selected_record.date,
            'hour': selected_record.time.hour,
            'minute': selected_record.time.minute,
            'violation': selected_record.violation,
            'status': selected_record.status,
            'location': selected_record.location,
            'officer': selected_record.officer.username if selected_record.officer else ""
        }
        form = ReportForm(initial=initial_data)

        if request.method == 'POST':
            form = ReportForm(request.POST, request.FILES, instance=selected_record)
            if form.is_valid():
                form.save()

                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                saved_files = []

                for media_file in request.FILES.getlist('media'):
                    _, file_extension = os.path.splitext(media_file.name)
                    unique_filename = str(uuid.uuid4()) + file_extension
                    fs.save(unique_filename, media_file)
                    saved_files.append(unique_filename)

                removed_media = request.POST.get('removed_media', '').split(';')
                update_media_files(selected_record_id, saved_files, removed_media)

                messages.success(request, "记录和媒体文件已成功更新。")
                return redirect('edit_report')

    context = {
        'user_records': user_records,
        'selected_record': selected_record,
        'form': form,
        'media_urls': media_urls,
    }
    return render(request, 'reports/edit_report.html', context)
@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

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
                officer=request.user if form.cleaned_data['officer'] else None,
                # traffic_violation_id
                username=request.user.username
            )
            traffic_violation.save()

            # Handle file uploads
            for file in request.FILES.getlist('media'):
                # Save file to FileSystemStorage
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_url = fs.url(filename)

                # Create and save MediaFile instance
                MediaFile.objects.create(
                    traffic_violation=traffic_violation,
                    file=file_url
                )

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')
    else:
        form = ReportForm()

    return render(request, 'reports/dashboard.html', {'form': form})