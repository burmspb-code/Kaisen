from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """Кастомный бэкенд для аутентификации пользователей по email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Извлекаем email из аргументов (Django может передать его как username)
        email = kwargs.get('email', username)

        try:
            # Ищем пользователя по email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        # Проверяем хэш пароля и активность аккаунта
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
