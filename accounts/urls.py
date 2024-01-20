from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # WEB url
    path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('account/', views.account_view, name='account'),
    path('validate-username-email/', views.validate_username_email, name='validate-username-email'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/change/', views.custom_password_change, name='password_change'),
    path('password/change/done/', views.password_change_done, name='password_change_done'),
    path('email/change/', views.email_change, name='email_change'),
    path('social-connections/', views.social_account_connections, name='socialaccount_connections'),
    path('delete-account/', views.account_delete, name='account_delete'),
    # path('', include('allauth.urls')),
    # path('accounts/', include('allauth.urls')),

    # API url
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
    path('register/', views.register_api, name='api_register'),
    path('api/verify/', views.verify_api, name='api_verify'),
    path('api/account/', views.account_api, name='api_account'),
    path('api/validate-username-email/', views.validate_username_email, name='api_validate-username-email'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/password/change/', views.custom_password_change_api, name='api_password_change'),
    path('api/password/change/done/', views.password_change_done_api, name='api_password_change_done'),
    path('api/email/change/', views.email_change_api, name='api_email_change'),
    path('api/social-connections/', views.social_account_connections_api, name='api_socialaccount_connections'),
    path('api/delete-account/', views.account_delete_api, name='api_account_delete'),
    # path('', include('allauth.urls')),
    # path('accounts/', include('allauth.urls')),
]