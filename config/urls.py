"""
Глобальный конфигурационный файл маршрутов (URL) всего проекта.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Изолируем API префиксом api/v1/
    path("api/v1/", include("users.urls", namespace="users")),

    # ================= МАРШРУТЫ АВТОДОКУМЕНТАЦИИ API =================
    # Скачивание файла схемы (нужно для работы панелей)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"),
    # Интерактивная панель Swagger UI (Рекомендуется)
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Альтернативная панель Redoc
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
]
