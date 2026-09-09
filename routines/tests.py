"""Модуль автоматического тестирования для приложения Routines."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from routines.models import Habit
from routines.services import send_telegram_habit_alert
from routines.tasks import send_habit_reminders

User = get_user_model()


# ================= Тестирование приложение Routines ========================

class HabitTestCase(APITestCase):
    """Тестирование пагинации, приватности и валидации привычек."""

    def setUp(self):
        """Первоначальная настройка перед каждым тестом."""
        # Создаем тестовых пользователей
        self.user_owner = User.objects.create_user(
            email="owner@example.com",
            password="OwnerPassword123!", # noqa: S106
            tg_chat_id="123456789",
        )
        self.user_stranger = User.objects.create_user(
            email="stranger@example.com",
            password="StrangerPassword123!", # noqa: S106
            tg_chat_id="987654321",
        )

        # Наполняем базу 10-ю топовыми привычками для проверки пагинации
        self.habits = []
        for i in range(10):
            habit = Habit.objects.create(
                user=self.user_owner,
                action=f"Атомная привычка разработчика №{i + 1}",
                location="Рабочее место",
                time_at="10:00:00",
                sign_pleasant_habit=False,
                periodicity=1,
                award="Квадратик шоколада",
                time_to_complete=timedelta(seconds=30),
                is_publicity=True,
            )
            self.habits.append(habit)

        # Генерируем URL-пути эндпоинтов
        self.list_url = reverse("routines:routines-list")
        self.create_url = reverse("routines:habit-create")
        # URL для деталей первой созданной привычки владельца
        self.detail_url = reverse(
            "routines:habit-detail", kwargs={"pk": self.habits[0].pk}
        )

    def test_habit_list_pagination(self):
        """Проверка работы пагинации (ровно по 5 элементов на страницу)."""
        # Авторизуем владельца
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем структуру ответа пагинации
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertEqual(response.data["count"], 10)
        # На первой странице должно быть строго 5 элементов
        self.assertEqual(len(response.data["results"]), 5)

    def test_habit_crud_privacy(self):
        """Проверка изоляции данных: чужой пользователь получает 404."""
        # Авторизуем постороннего пользователя
        self.client.force_authenticate(user=self.user_stranger)

        # Попытка прочесть чужую привычку
        response_get = self.client.get(self.detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)

        # Попытка изменить чужую привычку
        response_patch = self.client.patch(
            self.detail_url, data={"action": "Хакерская атака"}
        )
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND)

        # Попытка удалить чужую привычку
        response_delete = self.client.delete(self.detail_url)
        self.assertEqual(
            response_delete.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_validator_pleasant_habit_cannot_have_award(self):
        """Проверка бизнес-валидатора: у приятной привычки не может быть награды."""
        self.client.force_authenticate(user=self.user_owner)

        # Некорректные данные: приятная привычка с вознаграждением
        bad_data = {
            "action": "Посмотреть мем про Python",
            "location": "Смартфон",
            "time_at": "12:00:00",
            "sign_pleasant_habit": True,
            "periodicity": 1,
            "award": "Чашка кофе",  # Нарушение бизнес-правила!
            "time_to_complete": "00:00:30",
        }

        response = self.client.post(self.create_url, data=bad_data, format="json")
        # Ожидаем блокировку запроса
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "У приятной привычки не может быть вознаграждения или связанной привычки.",
            str(response.data),
        )

    @patch("requests.post")
    def test_telegram_notification_service_success(self, mock_post):
        """Проверяем успешную отправку уведомления через Mock-запрос."""
        # 1. Имитируем, что Telegram API ответил статусом 200 OK
        mock_post.return_value.status_code = 200

        # Находим тестовую привычку, созданную в setUp
        habit = self.habits[0]

        # 2. Запускаем сервис отправки
        result = send_telegram_habit_alert(habit_id=habit.id)

        # 3. Проверяем, что функция вернула True и requests.post был вызван
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("routines.tasks.send_single_telegram_notification.delay")
    def test_celery_tasks_integration(self, mock_task_delay):
        """Проверяем, что Celery Beat корректно находит привычки и генерирует подзадачи."""
        # Настраиваем время одной из привычек на текущее, чтобы сервис её нашёл
        import datetime
        now = datetime.datetime.now().time().strftime("%H:%M:00")
        habit = self.habits[0]
        habit.time_at = now
        habit.save()

        # Запускаем главную задачу планировщика
        send_habit_reminders()

        # Проверяем, что асинхронный вызов подзадачи сработал ровно 1 раз для этой привычки
        mock_task_delay.assert_called_once_with(habit.id)


# ================= Тестирование приложение Users ========================

class UsersTestCase(APITestCase):
    """Тестирование аутентификации, регистрации и профиля пользователей."""

    def setUp(self):
        """Первоначальная настройка перед каждым тестом."""
        self.register_url = reverse("users:user-register")
        self.login_url = reverse("users:auth-login")
        self.profile_url = reverse("users:user-profile")

        self.test_email = "test_user@example.com"
        self.test_password = "SecurePassword123!" # noqa: S105
        self.test_tg_chat_id = "123456789"

    def test_user_registration(self):
        """Проверка успешной регистрации нового пользователя через API."""
        data = {
            "email": "new_user@example.com",
            "password": "NewSecurePassword123!",
            "tg_chat_id": "987654321",
        }
        response = self.client.post(self.register_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="new_user@example.com").exists()
        )

    def test_user_login(self):
        """Проверка успешного входа пользователя в систему."""
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            tg_chat_id=self.test_tg_chat_id,
        )

        data = {"email": self.test_email, "password": self.test_password}
        response = self.client.post(self.login_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ИСПРАВЛЕНО: Безопасно проверяем наличие ключа в словаре, игнорируя регистр
        response_keys = [key.lower() for key in response.data.keys()]
        self.assertIn("token", response_keys)

    def test_user_profile_access(self):
        """Проверка просмотра профиля авторизованным пользователем."""
        user = User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            tg_chat_id=self.test_tg_chat_id,
        )

        # Принудительно авторизуем пользователя в тестовом клиенте
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.test_email)

    def test_custom_management_command_csu(self):
        """Тестирование консольной команды csu для создания суперпользователя."""
        # Очищаем базу от прошлых суперпользователей перед тестом
        User.objects.filter(is_superuser=True).delete()

        # Запуск команды csu
        call_command("csu")

        # ИСПРАВЛЕНО: Вместо хардкода email ищем созданного админа по его роли
        admin_user = User.objects.get(is_superuser=True)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
