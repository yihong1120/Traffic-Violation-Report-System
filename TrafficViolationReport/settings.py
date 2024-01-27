from datetime import timedelta
from pathlib import Path
import os
from django.conf import settings

# Maximum size in bytes before a file is handled in the file system
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024*1024*100  # 100MB

# Maximum size of request data (post body)
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024*1024*100  # 100MB

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Construct the full path to the media folders
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'reports' / 'media'

# Construct the full path to the error images folders
ERROR_IMAGE_URL = '/error_images/'
ERROR_IMAGE_ROOT = BASE_DIR / 'error_images'

# Construct the full path to the pivotal-equinox-404812-6722b643b8f4.json file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, 'static', 'pivotal-equinox-404812-6722b643b8f4.json')

# Development Settings - Not suitable for production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No 'SECRET_KEY' set in the environment.")

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("No 'GOOGLE_MAPS_API_KEY' set in the environment.")

DEBUG = False
ALLOWED_HOSTS = ['pivotal-equinox-404812.de.r.appspot.com', 'localhost', '127.0.0.1']

SESSION_COOKIE_AGE = 10800  # 3 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'reports',
    'accounts',
    'utils',
    'traffic_data',
    'license_plate_insights',
    'llm_customer_service',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'TrafficViolationReport.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TrafficViolationReport.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 允許所有域名進行跨域請求
CORS_ALLOW_ALL_ORIGINS = True

# 或者，只允許特定域名
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  # 允許的前端伺服器地址
#     "http://127.0.0.1:3000",
# ]

# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static_root/'
STATIC_ROOT = BASE_DIR / 'static_root'  # Directory for collectstatic to collect static files

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login and Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
if not EMAIL_HOST_USER:
    raise ValueError("No 'EMAIL_HOST_USER' set in the environment.")

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
if not EMAIL_HOST_PASSWORD:
    raise ValueError("No 'EMAIL_HOST_PASSWORD' set in the environment.")

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
if not DEFAULT_FROM_EMAIL:
    raise ValueError("No 'DEFAULT_FROM_EMAIL' set in the environment.")

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # or 'optional' or 'none'


# Django REST Framework 設定
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 其他設定...
}

# 在 settings.py 文件中添加或更新 SIMPLE_JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # 访问 token 的有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 刷新 token 的有效期
    'ROTATE_REFRESH_TOKENS': False,  # 如果为 True，每次刷新 token 时都会创建一个新的 refresh token
    'BLACKLIST_AFTER_ROTATION': True,  # 如果为 True，在刷新 token 后，旧的 refresh token 会被加入黑名单

    'ALGORITHM': 'HS256',  # 使用的签名算法
    'SIGNING_KEY': settings.SECRET_KEY,  # 用于签名 token 的密钥
    'VERIFYING_KEY': None,  # 用于验证 token 签名的密钥，如果与 SIGNING_KEY 相同，可以设置为 None

    'AUTH_HEADER_TYPES': ('Bearer',),  # 用于在 HTTP 头中表示 token 类型的字符串
    'USER_ID_FIELD': 'id',  # 用户模型中作为用户唯一标识的字段
    'USER_ID_CLAIM': 'user_id',  # token 负载中表示用户 ID 的字段

    # ... 如果有其他配置，可以继续添加 ...
}

# CORS 設定
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:3000",  # Flutter app 的 URL
    # 其他允許的來源...
]

# Celery 配置
CELERY_BEAT_SCHEDULE = {
    'delete-expired-unverified-users-every-hour': {
        'task': 'accounts.tasks.delete_expired_unverified_users',
        'schedule': timedelta(hours=1),
    },
}
'''
celery -A TrafficViolationReport worker --loglevel=info
celery -A TrafficViolationReport beat --loglevel=info
'''