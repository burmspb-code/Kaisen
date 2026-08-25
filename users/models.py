"""
Модуль моделей приложения управления пользователями (users).

Содержит кастомную модель пользователя CustomUser, расширяющую стандартный
функционал Django возможностью хранения аватаров.

Применяется в качестве глобальной модели аутентификации проекта
через настройку AUTH_USER_MODEL в settings.py.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    username = None
    email = models.EmailField(
        unique=True, verbose_name="email", help_text="Введите адрес электронной почты"
    )
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="avatars",
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"  # Поле для входа (логин)
    REQUIRED_FIELDS = []

    # Подключаем кастомный менеджер (без него не создастся суперпользователь)
    objects = CustomUserManager()

    class Meta:
        """Класс метаданных."""

        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.email}"
