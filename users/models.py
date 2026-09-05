"""
Модели приложения users.

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
    tg_chat_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Telegram Chat ID",
        help_text="ID чата пользователя в Телеграм для отправки уведомлений",
    )

    USERNAME_FIELD = "email"  # Поле для входа (логин)
    REQUIRED_FIELDS = ()

    # Подключаем кастомный менеджер (без него не создастся суперпользователь)
    objects = CustomUserManager()

    class Meta:
        """Класс метаданных."""

        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.email}"
