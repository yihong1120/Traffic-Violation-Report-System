from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import UserProfile
from .models import TrafficViolation, MediaFile
from django.contrib import messages
import random
from google.cloud import bigquery
import googlemaps
import os, re
from pathlib import Path
import json

# BASE_DIR is defined in settings.py as the path to the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Constructing the full path to the config.json file
config_path = BASE_DIR / 'static' / 'config.json'

# Opening the configuration file using the constructed path
with open(config_path) as config_file:
    config = json.load(config_file)

# SECURITY WARNING: keep the secret key used in production secret!
GoogleMaps_API_KEY = config.get('GoogleMaps_API_KEY')
if not GoogleMaps_API_KEY:
    raise ValueError("No 'GoogleMaps_API_KEY' set in configuration.")

def home(request):
    return render(request, 'reports/home.html')

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
        gmaps = googlemaps.Client(key=GoogleMaps_API_KEY)
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

            # 指定你的服务帐户文件路径
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "static/pivotal-equinox-404812-6722b643b8f4.json"

            # 创建 BigQuery 客户端
            client = bigquery.Client()

            # 指定你的 dataset ID 和 table ID
            project_id = "pivotal-equinox-404812"
            dataset_id = "traffic_violation_db"
            table_id = "reports_trafficviolation"

            # 创建 Dataset 和 Table 的引用
            dataset_ref = client.dataset(dataset_id, project=project_id)
            table_ref = dataset_ref.table(table_id)

            # 获取 Table 对象
            table = client.get_table(table_ref)  # API 请求

            # 准备要插入的数据
            rows_to_insert = [
                {
                    "license_plate": traffic_violation.license_plate,
                    "date": traffic_violation.date.strftime("%Y-%m-%d"),  # 格式化日期为字符串
                    "time": traffic_violation.time.strftime("%H:%M:%S"),  # 格式化时间为字符串
                    "violation": traffic_violation.violation,
                    "status": traffic_violation.status,
                    "location": traffic_violation.location,
                    "officer": traffic_violation.officer.username if traffic_violation.officer else None,  # 使用 officer 的用户名或 None
                },
                # 可以添加更多的行
            ]

            # 使用 insert_rows_json 方法插入数据
            errors = client.insert_rows_json(table, rows_to_insert)

            # 检查有没有发生错误
            if errors == []:
                print("New rows have been added.")
            else:
                print("Errors occurred:", errors)

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')  # 重定向到dashboard页面或其他页面
    else:
        form = ReportForm()  # 如果不是POST请求，则创建一个空表单

    return render(request, 'reports/dashboard.html', {'form': form})