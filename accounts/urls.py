from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('account/', views.account_view, name='account'),
    path('validate-username-email/', views.validate_username_email, name='validate-username-email'),
    # 包含 allauth 的 URL
    path('', include('allauth.urls')),
]