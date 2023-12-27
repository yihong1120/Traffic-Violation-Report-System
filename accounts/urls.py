from django.urls import path
from .views import UserProfileView  # 假设您有一个API视图用于用户资料
# 导入其他API相关的视图

app_name = 'accounts_api'

urlpatterns = [
    path('user-profile/', UserProfileView.as_view(), name='user-profile'),
    # 定义其他API路由...
    # 例如:
    # path('some-api-view/', SomeApiView.as_view(), name='some-api-view'),
]
