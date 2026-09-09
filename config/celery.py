"""Конфигурационный модуль Celery для проекта Kaisen."""

import os

from celery import Celery

# 1. Устанавливаем настройки Django по умолчанию для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2. Инициализируем приложение Celery под именем 'celery'
# Это избавляет от необходимости дописывать ':app' в терминале
celery = Celery("kaisen")

# 3. Считываем конфигурацию из settings.py с префиксом CELERY_
celery.config_from_object("django.conf:settings", namespace="CELERY")

# 4. Автоматически ищем фоновые задачи (tasks.py) во всех установленных приложениях
celery.autodiscover_tasks()
