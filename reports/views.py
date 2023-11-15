from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import UserProfile
from .models import TrafficViolation, MediaFile
import random
from google.cloud import bigquery
from django.http import JsonResponse
from .bigquery_utils import get_traffic_violations, save_to_bigquery
import googlemaps
import os, re

def get_traffic_violation_view(request):
    data = get_traffic_violations()
    return JsonResponse(data, safe=False)

def home(request):
    context = {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY}
    return render(request, 'reports/home.html', context)

def login(request, *args, **kwargs):
    # 如果用戶已登入，重定向到首頁
    if request.user.is_authenticated:
        return redirect('home')
    return LoginView.as_view()(request, *args, **kwargs)

def generate_random_code():
    return ''.join(random.choice('0123456789') for _ in range(6))

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # 保存用戶模型實例
            print("yes")
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

def is_address(address):
    pattern = re.compile(r"[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]-[0-9]+")
    return pattern.search(address)

def get_latitude_and_longitude(address):
    if is_address(address):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        geocode_result = gmaps.geocode(address)

        # Check if geocode_result is not empty
        if not geocode_result:
            return None, None

        # Access the first element of the list and then the 'location' key
        location = geocode_result[0]['geometry']['location']
        return location['lng'], location['lat']
    else:
        return None, None

def process_input(input_string):
    lat, lng = get_latitude_and_longitude(input_string)
    if lat is not None and lng is not None:
        return f"{lng},{lat}"
    else:
        return input_string

@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # 创建一个新的 TrafficViolation 实例
            traffic_violation = TrafficViolation(
                license_plate=form.cleaned_data['license_plate'],
                date=form.cleaned_data['date'],
                time=form.cleaned_data['time'],  # 使用表单中清洗过的 time 字段
                violation=form.cleaned_data['violation'],
                status=form.cleaned_data['status'],
                location=process_input(form.cleaned_data['location']),
                officer=form.cleaned_data['officer'] if form.cleaned_data['officer'] else None,
                # media 字段将在模型的 save 方法中处理
            )
            # 保存 TrafficViolation 实例
            traffic_violation.save()

            # Now handle file uploads
            for file in request.FILES.getlist('media'):
                # Create a new instance of a model that handles the media files
                # This model should have a ForeignKey to `TrafficViolation` and a FileField
                media_instance = MediaFile(
                    traffic_violation=traffic_violation,
                    file=file
                )
                media_instance.save()

            # Insert the data from form into BigQuery
            save_to_bigquery(traffic_violation)

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')  # 重定向到dashboard页面或其他页面
    else:
        form = ReportForm()  # 如果不是POST请求，则创建一个空表单

    return render(request, 'reports/dashboard.html', {'form': form})