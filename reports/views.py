from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import UserProfile
from .models import TrafficViolation, MediaFile
from .utils import is_address, get_latitude_and_longitude, process_input, generate_random_code
from google.cloud import bigquery
from .bigquery_utils import get_traffic_violation_markers, get_traffic_violation_details, save_to_bigquery, search_traffic_violations

def search_traffic_violations_view(request):
    client = bigquery.Client()

    keyword = request.GET.get('keyword', '')
    time_range = request.GET.get('timeRange', 'all')
    from_date = request.GET.get('fromDate', '')
    to_date = request.GET.get('toDate', '')

    data = search_traffic_violations(client, keyword, time_range, from_date, to_date)

    return JsonResponse(data, safe=False)

def traffic_violation_markers_view(request):
    data = get_traffic_violation_markers()
    return JsonResponse(data, safe=False)

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

@login_required
def edit_report(request):
    client = bigquery.Client()
    username = request.user.username

    # 从 BigQuery 获取当前用户的提交记录
    query = (
        f"SELECT * FROM `pivotal-equinox-404812.traffic_violation_db.reports_trafficviolation` "
        f"WHERE username = '{username}'"
    )
    query_job = client.query(query)
    user_records = [dict(row) for row in query_job.result()]  # 转换为字典列表

    # 从 BigQuery 获取媒体文件记录
    media_query = (
        "SELECT * FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` "
        "LIMIT 1000"
    )
    media_query_job = client.query(media_query)
    media_records = [dict(row) for row in media_query_job.result()]  # 转换为字典列表

    # 将媒体文件匹配到相应的违规记录中
    for record in user_records:
        record_media = [media['file'] for media in media_records if media['traffic_violation_id'] == record['traffic_violation_id']]
        record['media'] = record_media

    # 如果用户选择编辑特定的记录
    selected_record_id = request.GET.get('record_id')
    if selected_record_id:
        selected_record = next((record for record in user_records if str(record['traffic_violation_id']) == selected_record_id), None)
        if selected_record:
            # 创建一个表单实例，使用选中记录的数据进行初始化
            form = ReportForm(initial=selected_record)
            if request.method == 'POST':
                # 处理POST请求，如果数据有效，更新记录
                form = ReportForm(request.POST, request.FILES)
                if form.is_valid():
                    # 提取表单数据
                    data = form.cleaned_data

                    # 构建更新语句
                    update_query = """
                        UPDATE `pivotal-equinox-404812.traffic_violation_db.reports_trafficviolation`
                        SET license_plate = @license_plate, 
                            date = @date, 
                            time = @time, 
                            violation = @violation, 
                            status = @status, 
                            location = @location, 
                            officer = @officer
                        WHERE traffic_violation_id = @traffic_violation_id
                    """

                    # 配置查询参数
                    params = [
                        bigquery.ScalarQueryParameter("license_plate", "STRING", data['license_plate']),
                        bigquery.ScalarQueryParameter("date", "DATE", data['date']),
                        bigquery.ScalarQueryParameter("time", "STRING", data['time'].strftime("%H:%M:%S")),
                        bigquery.ScalarQueryParameter("violation", "STRING", data['violation']),
                        bigquery.ScalarQueryParameter("status", "STRING", data['status']),
                        bigquery.ScalarQueryParameter("location", "STRING", data['location']),
                        bigquery.ScalarQueryParameter("officer", "STRING", data['officer']),
                        bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
                    ]

                    job_config = bigquery.QueryJobConfig(
                        query_parameters=params
                    )

                    # 执行更新语句
                    query_job = client.query(update_query, job_config=job_config)
                    query_job.result()  # 等待执行完成

                    # 获取媒体文件
                    media_files = request.FILES.getlist('media')

                    # 删除旧的媒体文件记录
                    delete_query = """
                        DELETE FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile`
                        WHERE traffic_violation_id = @traffic_violation_id
                    """
                    delete_params = [
                        bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
                    ]
                    delete_job_config = bigquery.QueryJobConfig(
                        query_parameters=delete_params
                    )
                    client.query(delete_query, delete_job_config).result()

                    # 为每个文件构建并执行插入语句
                    for media_file in media_files:
                        insert_query = """
                            INSERT INTO `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` (file, traffic_violation_id)
                            VALUES (@file, @traffic_violation_id)
                        """
                        insert_params = [
                            bigquery.ScalarQueryParameter("file", "STRING", media_file.name),
                            bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
                        ]
                        insert_job_config = bigquery.QueryJobConfig(
                            query_parameters=insert_params
                        )
                        client.query(insert_query, insert_job_config).result()

                    messages.success(request, "记录和媒体文件已成功更新。")
                    # 重定向或其他后续操作

        else:
            form = None
    else:
        form = None

    context = {
        'user_records': user_records,
        'selected_record': selected_record if selected_record_id else None,
        'form': form,
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
            # 创建一个新的 TrafficViolation 实例
            traffic_violation = TrafficViolation(
                license_plate=form.cleaned_data['license_plate'],
                date=form.cleaned_data['date'],
                time=form.cleaned_data['time'],  # 使用表单中清洗过的 time 字段
                violation=form.cleaned_data['violation'],
                status=form.cleaned_data['status'],
                location=process_input(form.cleaned_data['location']),
                officer=form.cleaned_data['officer'] if form.cleaned_data['officer'] else None,
                username=request.user.username  # 添加当前登录用户的用户名
                # media 字段将在模型的 save 方法中处理
            )
            # 保存 TrafficViolation 实例
            traffic_violation.save()

            # Now handle file uploads
            media_instances = []
            for file in request.FILES.getlist('media'):
                # Create a new instance of a model that handles the media files
                # This model should have a ForeignKey to `TrafficViolation` and a FileField
                media_instance = MediaFile(
                    traffic_violation=traffic_violation,
                    file=file
                )
                media_instance.save()
                media_instances.append(media_instance)

            # Insert the data from form into BigQuery
            save_to_bigquery(traffic_violation, media_instances)

            messages.success(request, '报告提交成功。')
            return redirect('dashboard')  # 重定向到dashboard页面或其他页面
    else:
        form = ReportForm()  # 如果不是POST请求，则创建一个空表单

    return render(request, 'reports/dashboard.html', {'form': form})