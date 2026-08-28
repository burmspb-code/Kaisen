import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """Консольная команда для безопасного создания суперпользователя из переменных окружения (.env)."""

    help = "Создает администратора системы, используя Email в качестве идентификатора."

    def handle(self, *args, **options):
        """Безопасно создает суперпользователя на основе данных из .env.

        Предотвращает дублирование учетных записей при повторном запуске.
        """
        User = get_user_model()

        # Используем getenv (он возвращает None, если переменной нет, и не бросает KeyError)
        email = os.getenv("ADMIN_EMAIL", "default_admin@example.com")
        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "Ошибка: В файле .env не задана переменная ADMIN_PASSWORD"
                )
            )
            return

        # Явная проверка через exists() — это быстрее и безопаснее для кастомных моделей
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name="admin",
                last_name="admin",
            )
            self.stdout.write(self.style.SUCCESS(f"Успешно создан админ: {email}"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь {email} уже существует в базе данных."
                )
            )
