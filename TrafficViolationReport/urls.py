from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from traffic_data.views import home
from reports.views import dashboard, edit_report
from accounts.views import login, register, account_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('edit-report/', edit_report, name='edit_report'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('account/', account_view, name='account_view'),
    # path('logout/', LogoutView.as_view(), name='logout'),

    path('reports/', include('reports.urls', namespace='reports')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # path('traffic_data/', include('traffic_data.urls', namespace='traffic_data')),
    path('', include('traffic_data.urls', namespace='traffic_data')),
    
    # 其他路徑...
]

# 在開發環境中服務媒體文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)