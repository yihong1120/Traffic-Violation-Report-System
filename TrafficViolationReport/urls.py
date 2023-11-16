"""
URL configuration for TrafficViolationReport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reports import views as report_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('traffic-violation-markers/', report_views.get_traffic_violation_markers, name='traffic-violation-markers'),
    path('traffic-violation-details/<int:traffic_violation_id>/', report_views.get_traffic_violation_details, name='traffic-violation-details'),
    # path('login/', LoginView.as_view(), name='login'),
    path('login/', report_views.login, name='login'),
    path('register/', report_views.register, name='register'),
    path('verify/', report_views.verify, name='verify'),
    path('account/', report_views.account_view, name='account'),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', report_views.home, name='home'),
    path('dashboard/', report_views.dashboard, name='dashboard'),
]

# 在开发环境中服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)