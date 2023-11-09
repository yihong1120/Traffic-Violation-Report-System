from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .forms import ReportForm
from .models import MyUser
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
            user = form.save()

            # 生成驗證碼
            code = generate_random_code()

            # 發送驗證郵件
            send_mail(
                subject="驗證台灣違規平台帳戶",
                body="請點擊以下連結驗證您的帳戶：\n\nhttp://localhost:8000/verify/?code={code}".format(code=code),
                from_email="trafficviolationtaiwan@gmail.com",
                recipient_list=[user.email],
            )

            return redirect('verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'reports/register.html', {'form': form})

def verify(request):
    # 從 URL 中獲取驗證碼
    code = request.GET.get('code')

    # 驗證驗證碼
    if not code:
        return render(request, 'reports/verify.html', {'error': '驗證碼無效'})

    # 驗證成功，更新使用者狀態
    if code == MyUser.objects.get(id=request.user.id).email_verified_code:
        user = MyUser.objects.get(id=request.user.id)
        user.email_verified = True
        user.email_verified_code = None
        user.save()
        return redirect('login')
    else:
        return render(request, 'reports/verify.html', {'error': '驗證碼錯誤'})

@login_required
def account_view(request):
    return render(request, 'reports/account.html', {'user': request.user})

@login_required
def dashboard(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: Save data to MySQL and GCP MySQL
            pass
    else:
        form = ReportForm()
    return render(request, 'reports/dashboard.html', {'form': form})