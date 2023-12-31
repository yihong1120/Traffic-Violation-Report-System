from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from traffic_data.views import home
from reports.views import dashboard, edit_report
from accounts.views import login, register, account_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 包含您的應用的 urls
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('edit-report/', edit_report, name='edit_report'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('account/', account_view, name='account_view'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('reports/', include('reports.urls', namespace='reports')),
    path('api/accounts/', include('accounts.urls')),  # API路由
    path('accounts/', include('accounts.web_urls', namespace='accounts')),  # 传统视图路由
    path('', include('traffic_data.urls', namespace='traffic_data')),
    path('license_plate_insights/', include('license_plate_insights.urls', namespace='license_plate_insights')),
    path('llm_customer_service/', include('llm_customer_service.urls', namespace='llm_customer_service')),

]

# 在開發環境中服務媒體文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)