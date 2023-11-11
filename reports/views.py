from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import UserProfile
from django.contrib import messages
import mysql.connector

import random

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

@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()  # 将数据保存到 Django 默认的数据库

            # TODO: 这里添加将数据保存到 GCP MySQL 的代码
            # 您需要根据您的情况来填写下面的连接参数
            # 这个部分的代码只是一个框架，您需要实现实际的数据插入逻辑
            try:
                # 连接到 GCP MySQL 数据库
                conn = mysql.connector.connect(
                    user='your_gcp_mysql_user',
                    password='your_gcp_mysql_password',
                    host='your_gcp_mysql_host',
                    database='your_gcp_mysql_database'
                )
                cursor = conn.cursor()

                # 编写 SQL 插入命令，这需要根据您的数据模型来定制字段和表名
                insert_query = "INSERT INTO your_table_name (field1, field2, ...) VALUES (%s, %s, ...)"
                report_data = (report.field1, report.field2, ...)

                cursor.execute(insert_query, report_data)
                conn.commit()
            except mysql.connector.Error as err:
                messages.error(request, '保存到 GCP MySQL 失败: {}'.format(err))
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

            messages.success(request, '报告提交成功')
            return redirect('some_success_url')  # 提交成功后的重定向
    else:
        form = ReportForm()

    return render(request, 'reports/dashboard.html', {'form': form})