from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import EmailChangeForm
from .forms import CustomUserCreationForm
from .models import UserProfile
from utils.utils import generate_random_code
from django.utils import timezone
import datetime
from .serializers import UserProfileSerializer


@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        auth_login(request, user)

        # 确保 UserProfile 存在
        UserProfile.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return Response({'error': 'Invalid Credentials'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 确保用户是通过 JWT 认证的
def logout_api(request):
    try:
        # 确保请求体中包含刷新令牌
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token not provided.'}, status=400)
        
        token = RefreshToken(refresh_token)
        
        # 将 JWT 加入黑名单
        token.blacklist()

        return Response(status=HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info_api(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({"error": f"UserProfile not found for user: {request.user.username}"}, status=404)
    
    
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
        # 在这里创建 UserProfile
        UserProfile.objects.get_or_create(user=user)  # 使用 get_or_create 避免重复创建

        user = authenticate(username=user.username, password=form.cleaned_data['password1'])
        if user is not None:
            auth_login(request, user)
            refresh = RefreshToken.for_user(user)  # 创建 JWT token
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
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
        refresh = RefreshToken.for_user(user)  # 创建 JWT token
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Your account has been verified successfully.'
        })
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def account_delete_api(request):
    try:
        # 获取 JWT 的 Refresh Token
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        
        # 将 JWT 加入黑名单
        token.blacklist()

        # 删除用户账户
        request.user.delete()
        return Response({'message': 'Your account has been deleted successfully.'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


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
    )