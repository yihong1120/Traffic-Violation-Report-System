from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views, api_views, social_api_views

app_name = 'accounts'

urlpatterns = [
    # Web path
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

    # Accounts API path
    path('api/login/', api_views.login_api, name='api_login'),
    path('api/logout/', api_views.logout_api, name='api_logout'),
    path('api/get-user-info/', api_views.get_user_info_api, name='api_get_user_info'),
    path('api/register/', api_views.register_api, name='api_register'),
    path('api/verify/', api_views.verify_api, name='api_verify'),
    path('api/account/', api_views.account_api, name='api_account'),
    path('api/validate-username-email/', views.validate_username_email, name='api_validate_username_email'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/password-change/', api_views.custom_password_change_api, name='api_password_change'),
    path('api/password-change-done/', api_views.password_change_done_api, name='api_password_change_done'),
    path('api/email-change/', api_views.email_change_api, name='api_email_change'),
    path('api/delete-account/', api_views.account_delete_api, name='api_account_delete'),

    # Social Accounts API path
    path('api/social-connections/', social_api_views.social_account_connections_api, name='api_socialaccount_connections'),
    path('api/available-providers/', social_api_views.available_providers_api, name='api_available_providers'),
    path('api/disconnect-account/', social_api_views.disconnect_account_api, name='api_disconnect_account'),
    path('api/social/login/<str:provider_id>/', social_api_views.social_login_api, name='api_social_login'),
]