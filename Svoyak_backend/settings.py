"""
Django settings for Svoyak_backend project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os

from pathlib import Path

import channels.layers
import channels_redis.core
import corsheaders.middleware
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import django.contrib.sessions.middleware
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '13fcf*jdjk89ht8#e5g_7(wzye4$k3rth@lmb1342dztr!))pt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

DJANGO_CONTRIB_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'channels',
    'django_extensions',
    'django_property_filter',
    'drf_yasg',
]

PROJECT_APPS = [
    'core.players.apps.PlayersConfig',
    'core.rooms.apps.RoomsConfig',
    'core.packs.apps.PacksConfig',
]

INSTALLED_APPS = THIRD_PARTY_APPS + DJANGO_CONTRIB_APPS + PROJECT_APPS

MIDDLEWARE = [
    # 'core.players.middleware.CustomMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'Svoyak_backend.urls'

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

# WSGI_APPLICATION = 'Svoyak_backend.wsgi.application'
ASGI_APPLICATION = "Svoyak_backend.asgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)
print(DATABASES['default'])

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'players.Player'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'

# Extra lookup directories for collectstatic to find static files

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.players.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                os.environ.get('REDIS_URL', 'redis://:BigDen2001@c-c9qpqbdqpsa2jcrvt78e.rw.mdb.yandexcloud.net:6379')],
        },
    },
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

if DEBUG:
    # CORS_ALLOW_CREDENTIALS = True
    # CORS_ALLOW_ALL_ORIGINS = True
    # CORS_ALLOW_HEADERS = [
    #     'accept',
    #     'accept-encoding',
    #     'authorization',
    #     'content-type',
    #     'dnt',
    #     'origin',
    #     'user-agent',
    #     'x-csrftoken',
    #     'x-requested-with',
    #     'Access-Control-Allow-Headers',
    #     'Access-Control-Allow-Credentials',
    # ]
    # CORS_ALLOW_METHODS = [
    #     "DELETE",
    #     "GET",
    #     "OPTIONS",
    #     "PATCH",
    #     "POST",
    #     "PUT",
    # ]
    # CORS_ALLOWED_ORIGIN = [
    #     'http://localhost:3000'
    # ]
    # CORS_ORIGIN_WHITELIST = (
    #     'http://localhost:3000',
    #     'http://127.0.0.1:3000',
    #     'https://jolly-morse-6d6dc0.netlify.app'
    # )

    CORS_ORIGIN_ALLOW_ALL = True
    INSTALLED_APPS = ['corsheaders'] + INSTALLED_APPS
    MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE

TOKEN_HEADER_NAME = 'Authorization'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = "no-reply.svoyak@yandex.ru"
EMAIL_HOST_PASSWORD = "AndreevKarpov2"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# CELERY FOR EMAIL SENDING
CELERY_BROKER_URL = os.environ.get("REDIS_URL",
                                   'redis://:BigDen2001@c-c9qpqbdqpsa2jcrvt78e.rw.mdb.yandexcloud.net:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
