from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .forms import CustomUserCreationForm
from .models import UserProfile
from utils.utils import generate_random_code
from django.utils import timezone
import datetime


# 假設你有一個 EmailChangeForm 來處理電子郵件的更新
from .forms import EmailChangeForm

def login(request, *args, **kwargs):
    """
    登入視圖。如果用戶已登入，則重定向到首頁。
    """
    if request.user.is_authenticated:
        return redirect('home')
    return LoginView.as_view(template_name='accounts/login.html')(request, *args, **kwargs)


def validate_username_email(request):
    """
    AJAX 請求用來驗證用戶名和電子郵件是否已經存在。
    """
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'username_error': '這個用戶名已被使用' if User.objects.filter(username=username).exists() else None,
        'email_error': '這個電子郵件地址已被使用' if User.objects.filter(email=email).exists() else None,
    }
    return JsonResponse(data)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 设置验证码超时时间为30分钟后
            profile = UserProfile.objects.create(user=user, email_verified_code='your_code')
            profile.verification_code_expiry = timezone.now() + datetime.timedelta(minutes=30)
            profile.save()
            create_user_profile(user)
            return redirect('verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def create_user_profile(user):
    """
    為新註冊的用戶創建用戶資料檔。
    """
    code = generate_random_code()
    UserProfile.objects.create(user=user, email_verified_code=code)
    send_verification_email(user.email, code)


def send_verification_email(email, code):
    """
    發送包含驗證碼的電子郵件。
    """
    subject = "驗證您的帳戶"
    message = f"您的驗證碼是：{code}"
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, '請輸入驗證碼。')
            return render(request, 'accounts/verify.html')

        try:
            profile = UserProfile.objects.get(user=request.user, email_verified_code=code)
            if profile.is_verification_code_expired():
                messages.error(request, '驗證碼已過期。')
                return render(request, 'accounts/verify.html')
            profile.email_verified = True
            profile.email_verified_code = ''
            profile.save()
            messages.success(request, '您的帳戶已經成功驗證。')
            return redirect('login')
        except UserProfile.DoesNotExist:
            messages.error(request, '驗證碼錯誤。')
            return render(request, 'accounts/verify.html')
    else:
        return render(request, 'accounts/verify.html')



@login_required
def account_view(request):
    """
    顯示用戶的帳戶信息。
    """
    return render(request, 'accounts/account.html', {'user': request.user})

from .forms import EmailChangeForm

@login_required
def email_change(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email has been updated.')
            return redirect('profile')  # 假設有一個名為 'profile' 的 URL
    else:
        form = EmailChangeForm(instance=request.user)
    return render(request, 'account/email_change_form.html', {'form': form})

@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 更新 session 以保持用戶登入狀態
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('accounts:password_change_done')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change_form.html', {'form': form})

@login_required
def password_change_done(request):
    # 顯示密碼更改成功的消息
    return render(request, 'accounts/password_change_done.html')

@login_required
def social_account_connections(request):
    # 這裡的實現將取決於你如何處理社交帳號連結
    # 如果你使用 django-allauth，它已經提供了視圖來處理社交帳號連結
    # 以下是一個假設性的實現
    return render(request, 'accounts/social_connections.html')

@login_required
def account_delete(request):
    if request.method == 'POST':
        # 確認用戶真的想要刪除帳號
        # 這裡可以添加一個表單來讓用戶確認刪除操作
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')  # 假設有一個名為 'home' 的 URL
    return render(request, 'accounts/account_delete_confirm.html')