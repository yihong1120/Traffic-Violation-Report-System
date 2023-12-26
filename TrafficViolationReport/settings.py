"""
This file contains the settings for the Traffic Violation Report system. 
It includes configurations for installed apps, middleware, database, 
authentication, email, and other Django settings.
"""

from datetime import timedelta
from pathlib import Path
import os

# Maximum size in bytes before a file is handled in the file system
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024*1024*100  # 100MB

# Maximum size of request data (post body)
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024*1024*100  # 100MB

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Construct the full path to the media folders
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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

DEBUG = True
ALLOWED_HOSTS = []

SESSION_COOKIE_AGE = 10800  # 3 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports',
    'accounts',
    'utils',
    'traffic_data',
    'license_plate_insights',
    'llm_customer_service',
    'django.contrib.sites',
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
]

ROOT_URLCONF = 'TrafficViolationReport.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

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