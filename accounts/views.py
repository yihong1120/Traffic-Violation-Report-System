from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import UserProfile
from utils.utils import (
    generate_random_code, 
)


def login(request, *args, **kwargs):
    # 如果用戶已登入，重定向到首頁
    if request.user.is_authenticated:
        return redirect('home')
    # return LoginView.as_view()(request, *args, **kwargs)
    return LoginView.as_view(template_name='accounts/login.html')(request, *args, **kwargs)

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
    
    return render(request, 'accounts/register.html', {'form': form})

def verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, '請輸入驗證碼。')
            return render(request, 'accounts/verify.html')

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
        return render(request, 'accounts/verify.html')
    
@login_required
def account_view(request):
    return render(request, 'accounts/account.html', {'user': request.user})