"""
Маршрутизация (URL) приложения управления пользователями (users).
"""

from django.urls import path

from users.apps import UsersConfig
from users.views import UserListAPIView, UserLoginAPIView, UserLogoutAPIView, UserProfileAPIView, UserRegisterAPIView

app_name = UsersConfig.name

urlpatterns = [
    # Список пользователей
    path(
        "users/",
        UserListAPIView.as_view(),
        name="user-list",
    ),
    # Регистрация
    path(
        "users/register/",
        UserRegisterAPIView.as_view(),
        name="user-register",
    ),
    # Эндпоинты аутентификации
    path(
        "auth/login/",
        UserLoginAPIView.as_view(),
        name="auth-login",
    ),
    # Эндпоинт закрытия сессии
    path(
        "auth/logout/",
        UserLogoutAPIView.as_view(),
        name="auth-logout",
    ),
    path(
        "users/profile/",
        UserProfileAPIView.as_view(),
        name="user-profile",
    )
]
