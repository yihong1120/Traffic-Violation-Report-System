from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_204_NO_CONTENT
from .forms import CustomUserCreationForm
from .models import UserProfile
from utils.utils import generate_random_code
from django.utils import timezone
import datetime
from rest_framework.views import APIView
from .serializers import UserProfileSerializer

# 假設你有一個 EmailChangeForm 來處理電子郵件的更新
from .forms import EmailChangeForm

class UserProfileView(APIView):
    def get(self, request):
        profiles = UserProfile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)


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
            create_user_profile(user)

            # 使用 authenticate 和 login 函數來登入用戶
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)

            return redirect('accounts:verify')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def create_user_profile(user):
    """
    為新註冊的用戶創建用戶資料檔。
    """
    code = generate_random_code()
    verification_code_expiry = timezone.now() + datetime.timedelta(minutes=30)
    UserProfile.objects.create(
        user=user, 
        email_verified_code=code, 
        verification_code_expiry=verification_code_expiry
    )
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
            # 假設你的 UserProfile 模型有一個 user 屬性指向 User 模型
            profile = UserProfile.objects.get(email_verified_code=code)
            if profile.is_verification_code_expired():
                messages.error(request, '驗證碼已過期。')
                return render(request, 'accounts/verify.html')

            # 驗證碼正確，且未過期，則設置電子郵件已驗證
            profile.email_verified = True
            profile.email_verified_code = ''
            profile.save()

            # 自動登入用戶
            user = profile.user
            # 由於用戶已經通過電子郵件驗證，因此可以安全地登入用戶
            # 不需要再次檢查密碼，因為他們已經通過電子郵件驗證了他們的身份
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, '您的帳戶已經成功驗證。')
            return redirect('home')  # 或者重定向到你的首頁視圖
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

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        auth_login(request, user)
        token, _ = Token.objects.get_or_create(user=user)  # 这里不应该出现问题了
        return Response({'token': token.key})
    return Response({'error': 'Invalid Credentials'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        # 删除当前用户的认证 Token
        request.user.auth_token.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    except Token.DoesNotExist:
        return Response(status=HTTP_204_NO_CONTENT)

@api_view(['GET'])
def validate_username_email_api(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'username_error': 'This username is already in use.' if User.objects.filter(username=username).exists() else None,
        'email_error': 'This email is already in use.' if User.objects.filter(email=email).exists() else None,
    }
    return Response(data)

@api_view(['POST'])
def register_api(request):
    form = CustomUserCreationForm(request.data)
    if form.is_valid():
        user = form.save()
        user = authenticate(username=user.username, password=form.cleaned_data['password1'])
        if user is not None:
            auth_login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
    return Response(form.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_profile_api(request):
    code = generate_random_code()
    verification_code_expiry = timezone.now() + datetime.timedelta(minutes=30)
    profile, created = UserProfile.objects.get_or_create(
        user=request.user, 
        defaults={
            'email_verified_code': code, 
            'verification_code_expiry': verification_code_expiry
        }
    )
    # Normally, we should send an email only if the profile was created.
    if created:
        send_verification_email(request.user.email, code)
    return Response({'message': 'Profile created successfully' if created else 'Profile already exists'})

@api_view(['POST'])
def verify_api(request):
    code = request.data.get('code')
    try:
        profile = UserProfile.objects.get(email_verified_code=code)
        if profile.is_verification_code_expired():
            return Response({'error': 'Verification code is expired.'}, status=400)

        profile.email_verified = True
        profile.email_verified_code = ''
        profile.save()

        user = profile.user
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return Response({'message': 'Your account has been verified successfully.'})
    except UserProfile.DoesNotExist:
        return Response({'error': 'Invalid verification code.'}, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_api(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_change_api(request):
    form = EmailChangeForm(request.data, instance=request.user)
    if form.is_valid():
        form.save()
        return Response({'message': 'Your email has been updated successfully.'})
    else:
        return Response(form.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_password_change_api(request):
    form = PasswordChangeForm(request.user, request.data)
    if form.is_valid():
        user = form.save()
        # 更新 session 以保持用户登录状态
        update_session_auth_hash(request, user)
        return Response({'message': 'Your password has been updated successfully!'})
    else:
        return Response(form.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def password_change_done_api(request):
    # 只是返回一个确认信息
    return Response({'message': 'Your password has been changed successfully.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def social_account_connections_api(request):
    # 根据你的实际情况实现逻辑
    # 这里只是返回一个示例响应
    return Response({'message': 'Social account connections information.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def account_delete_api(request):
    request.user.delete()
    return Response({'message': 'Your account has been deleted successfully.'})
