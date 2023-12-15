from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
    # path('account/', views.account_view, name='account'),
    path('validate-username-email/', views.validate_username_email, name='validate-username-email'),
    path('logout/', LogoutView.as_view(), name='logout'),  # This function logs out the user and redirects them to the login page.
    # 包含 allauth 的 URL
    path('', include('allauth.urls')),
]