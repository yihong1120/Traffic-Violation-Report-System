"""
Django settings for TrafficViolationReport project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import json

# BASE_DIR is defined in settings.py as the path to the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Constructing the full path to the config.json file
config_path = BASE_DIR / 'static' / 'config.json'

# Opening the configuration file using the constructed path
with open(config_path) as config_file:
    config = json.load(config_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("No 'SECRET_KEY' set in configuration.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports',
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
        'DIRS': [],
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
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    # Add more paths here if you have more than one static directory
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email backend configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

# Retrieving and validating the email host user from the configuration
EMAIL_HOST_USER = config.get('EMAIL_HOST_USER')
if not EMAIL_HOST_USER:
    raise ValueError("No 'EMAIL_HOST_USER' has been set in the configuration.")

# Retrieving and validating the email host password from the configuration
EMAIL_HOST_PASSWORD = config.get('EMAIL_HOST_PASSWORD')
if not EMAIL_HOST_PASSWORD:
    raise ValueError("No 'EMAIL_HOST_PASSWORD' has been set in the configuration.")

# Enabling TLS for email security
EMAIL_USE_TLS = True

# Retrieving and validating the default sender email address from the configuration
DEFAULT_FROM_EMAIL = config.get('DEFAULT_FROM_EMAIL')
if not DEFAULT_FROM_EMAIL:
    raise ValueError("No 'DEFAULT_FROM_EMAIL' has been set in the configuration.")

# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend',]
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

api_key = "GOOGLE_MAPS_API_KEY"  # 确保在settings.py中定义了这个变量
GOOGLE_MAPS_API_KEY = 'your_google_maps_api_key'  # 从环境变量或安全的配置管理系统中获取

DATABASES = {
    'default': {
        # 您现有的本地数据库配置
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('DATABASE_NAME'),
        'USER': config.get('DATABASE_USER'),
        'PASSWORD': config.get('DATABASE_PASSWORD'),
        'HOST': config.get('DATABASE_HOST'),
        'PORT': config.get('DATABASE_PORT'),
    },
    'gcp': {
        # GCP MySQL数据库的配置
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('GCP_DATABASE_NAME'),
        'USER': config.get('GCP_DATABASE_USER'),
        'PASSWORD': config.get('GCP_DATABASE_PASSWORD'),
        'HOST': config.get('GCP_DATABASE_HOST'),
        'PORT': config.get('GCP_DATABASE_PORT'),
    }
}