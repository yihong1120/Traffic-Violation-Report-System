from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls', namespace='reports')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('reports.urls')),  # 假设 home 视图在 reports 应用程序中
]

# 在开发环境中服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)