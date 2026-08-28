"""
Глобальный конфигурационный файл маршрутов (URL) всего проекта.
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    # Изолируем API префиксом api/v1/
    path("api/v1/", include("users.urls", namespace="users")),
]
