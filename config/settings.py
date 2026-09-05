import os
from pathlib import Path

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from config.settings_utils import get_env

load_dotenv()



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('SECRET_KEY')

# ВАЛИДАЦИЯ: Проверяем, существует ли ключ
if not SECRET_KEY:
    raise ImproperlyConfigured("Переменная окружения SECRET_KEY не задана в файле .env!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Домены, с которых разрешено делать запросы
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    "drf_spectacular_sidecar",
    "drf_spectacular",

    'routines',
    'users',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("DB_NAME"),
        "USER": get_env("DB_USER"),
        "PASSWORD": get_env("DB_PASSWORD"),
        "HOST": get_env("DB_HOST"),
        "PORT": int(os.getenv("DB_PORT")),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    # Ваш кастомный бэкенд для входа по email:
    'users.authentication.EmailAuthBackend',
    # Оставляем стандартный бэкенд (для админки Django, где вход по username):
    'django.contrib.auth.backends.ModelBackend',
]


# Internationalization
LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Указываем Django использовать кастомную модель вместо встроенной
AUTH_USER_MODEL = "users.CustomUser"


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# Настройки CORS для локальной разработки SPA
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Порт по умолчанию для React / Next.js
    "http://localhost:5173",  # Порт по умолчанию для Vite (Vue 3 / Svelte)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Разрешаем передачу cookie и токенов авторизации
CORS_ALLOW_CREDENTIALS = True


# ====================== Базовые настройки Django REST Framework ====================
REST_FRAMEWORK = {
    # ЯВНО УКАЗЫВАЕМ СТИЛИ АВТОРИЗАЦИИ:
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Основной способ для API и логаута:
        'rest_framework.authentication.TokenAuthentication',
        # Оставляем сессии ТОЛЬКО для того, чтобы вы могли входить в аккаунт
        # внутри дебаг-панели BrowsableAPIRenderer:
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        # Ограничения для анонимных пользователей (по IP-адресу)
        'rest_framework.throttling.AnonRateThrottle',
        # Ограничения для авторизованных пользователей (по User ID)
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Считываем лимиты из .env. Если их там нет, ставим безопасные дефолты.
        'anon': os.environ.get('THROTTLE_RATE_ANON', '10/minute'),
        'user': os.environ.get('THROTTLE_RATE_USER', '1000/day'),
    }
}

# Настройки для автодокументации
SPECTACULAR_SETTINGS = {
    'TITLE': 'Kaisen Habits API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Описываем, как именно работает TokenAuthentication для Swagger
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'TokenAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Введите токен в формате: Token <ваш_токен>'
            }
        }
    },
    # Применяем эту схему ко всему проекту глобально
    'SECURITY': [{'TokenAuth': []}],
}

# ==============================================================================
# НАСТРОЙКИ CELERY И REDIS
# ==============================================================================

# URL-адрес для подключения к Redis (брокер сообщений)
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

# URL-адрес для хранения результатов выполнения задач в Redis
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# Часовой пояс для планировщика Celery (должен совпадать с Django)
CELERY_TIMEZONE = TIME_ZONE  # Берём значение из переменной TIME_ZONE вашего проекта

# Включаем отслеживание запуска задач
CELERY_TASK_TRACK_STARTED = True

# Тайм-аут для хранения результатов задач в Redis (в секундандах - 1 день)
CELERY_RESULT_EXPIRES = 86400

# Настройка планировщика
CELERY_BEAT_SCHEDULE = {
    # Название задачи (может быть любым)
    "send-reminders-every-minute": {
        # Точный путь к функции-задаче, которую мы пометили декоратором @shared_task
        "task": "routines.tasks.send_habit_reminders",
        # Расписание запуска: crontab(minute="*") означает "просыпаться каждую минуту"
        "schedule": crontab(minute="*"),
    },
}

CELERY_BEAT_CHECK_INTERVAL = 60  # Расписание запуска, секунды

# ==============================================================================