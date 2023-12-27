from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    path('account/', views.account_view, name='account'),
    path('validate-username-email/', views.validate_username_email, name='validate-username-email'),
    path('logout/', LogoutView.as_view(), name='logout'),  # This function logs out the user and redirects them to the login page.
    # path('password/change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password/change/', views.custom_password_change, name='password_change'),
    path('password/change/done/', views.password_change_done, name='password_change_done'),
    path('email/change/', views.email_change, name='email_change'),
    path('social-connections/', views.social_account_connections, name='socialaccount_connections'),
    path('delete-account/', views.account_delete, name='account_delete'),
    # path('', include('allauth.urls')),
    # path('accounts/', include('allauth.urls')),
]