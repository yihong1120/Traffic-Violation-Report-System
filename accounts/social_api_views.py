from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import UserProfile
from .serializers import SocialAccountSerializer
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp
from allauth.socialaccount.helpers import complete_social_login
from django.http import HttpRequest


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def social_account_connections_api(request):
    # 获取当前用户的所有社交账户
    social_accounts = SocialAccountSerializer.objects.filter(user=request.user)
    
    # 序列化社交账户
    serializer = SocialAccountSerializer(social_accounts, many=True)
    
    # 返回序列化的数据
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_providers_api(request):
    # 从 settings 中获取提供商列表
    providers = settings.SOCIAL_ACCOUNT_PROVIDERS
    providers_data = [{"id": provider, "name": provider.capitalize()} for provider in providers]
    return Response(providers_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_account_api(request):
    provider_id = request.data.get('provider_id')
    try:
        account = SocialAccount.objects.get(provider=provider_id, user=request.user)
        account.delete()
        return Response({'message': 'Social account disconnected successfully.'})
    except SocialAccount.DoesNotExist:
        return Response({'error': 'Social account not found.'}, status=404)


@api_view(['POST'])
def social_login_api(request, provider_id):
    provider = provider_id
    token = request.data.get('token')

    try:
        # 获取对应的SocialApp
        app = SocialApp.objects.get(provider=provider)
        token = SocialToken(app=app, token=token)

        # 创建一个临时的request对象
        request = HttpRequest()
        request.method = 'POST'
        request.META['SERVER_NAME'] = 'localhost'
        request.META['SERVER_PORT'] = '8000'

        # 尝试登录
        login = SocialLogin(token=token)
        login.state = SocialLogin.state_from_request(request)
        complete_social_login(request, login)

        # 检查用户是否有效
        if not login.is_existing:
            return Response({'error': 'User does not exist.'}, status=400)

        # 确保 UserProfile 存在
        UserProfile.objects.get_or_create(user=login.user)

        # 创建JWT tokens
        refresh = RefreshToken.for_user(login.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    except Exception as e:
        return Response({'error': f'Error during social authentication: {str(e)}'}, status=400)