from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls', namespace='reports')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('traffic_data/', include('traffic_data.urls', namespace='traffic_data')),
    ## AI model application
]

# 在开发环境中服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)