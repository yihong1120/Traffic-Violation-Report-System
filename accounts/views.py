from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .forms import CustomUserCreationForm
from .models import UserProfile
from utils.utils import generate_random_code


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
    """
    註冊新用戶。如果請求為POST，則處理表單提交。
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # 保存用戶模型實例
            create_user_profile(user)
            return redirect('verify')  # 確保有一個名為'verify'的URL映射
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
    """
    驗證用戶電子郵件地址。如果驗證碼匹配，則更新用戶資料檔。
    """
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
    """
    顯示用戶的帳戶信息。
    """
    return render(request, 'accounts/account.html', {'user': request.user})
