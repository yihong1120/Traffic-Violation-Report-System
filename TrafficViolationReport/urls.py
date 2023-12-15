from django.contrib import admin
from django.urls import path, include
# The requested commented-out code block appears to be already removed.
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls', namespace='reports')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('traffic_data/', include('traffic_data.urls', namespace='traffic_data')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('traffic_data.urls', namespace='traffic_data')),
]

# 在开发环境中服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)