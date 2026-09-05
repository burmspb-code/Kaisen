import os

import requests
from django.db.models import F
from django.db.models.functions import ExtractDay
from django.utils import timezone

from routines.models import Habit


def current_time_reminders() -> list[int]:
    """Возвращает плоский список ID привычек с учетом их периодичности."""
    now = timezone.localtime(timezone.now())
    current_time_str = now.time().strftime("%H:%M:00")
    today = now.date()

    # Фильтруем те, что подходят по времени и имеют заполненный Telegram ID
    queryset = Habit.objects.filter(time_at=current_time_str).exclude(
        user__tg_chat_id=""
    )

    # Извлекаем чистые дни из разницы дат через ExtractDay
    queryset_with_days = queryset.annotate(
        days_since_last_sent=ExtractDay(today - F("last_sent_date"))
    )

    # Отбираем привычки, готовые к отправке (новые или у которых подошел срок)
    ready_habits = queryset_with_days.filter(
        last_sent_date__isnull=True
    ) | queryset_with_days.filter(days_since_last_sent__gte=F("periodicity"))

    return list(ready_habits.values_list("id", flat=True))


def send_telegram_habit_alert(habit_id: int) -> bool:
    """Формирует текст сообщения и отправляет его пользователю в Telegram."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Ошибка: Переменная TELEGRAM_BOT_TOKEN не задана в .env")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Импортируем модель локально для защиты от циклических импортов
    from routines.models import Habit

    try:
        habit = Habit.objects.get(id=habit_id)
    except Habit.DoesNotExist:
        print(f"⚠️ Ошибка: Привычка с ID {habit_id} не найдена в базе данных.")
        return False

    # Собираем красивый текст сообщения
    message = (
        f"⏰ *Время выработать привычку!*\n\n"
        f"💪 *Действие:* {habit.action}\n"
        f"📍 *Место выполнения:* {habit.location or 'Не указано'}\n"
        f"⏳ *Время на выполнение:* {habit.time_to_complete or 'Не ограничено'}"
    )

    if habit.award:
        message += f"\n🎁 *Ваше вознаграждение:* {habit.award}"

    payload = {
        "chat_id": habit.user.tg_chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            # Обновляем дату последней отправки сегодняшним числом
            habit.last_sent_date = timezone.now().date()
            habit.save(update_fields=["last_sent_date"])  # Оптимизированное сохранение одного поля

            print(f"✅ Уведомление по привычке {habit_id} успешно отправлено!")
            return True

        print(f"⚠️ Ошибка Telegram API ({response.status_code}): {response.text}")
        return False

    except requests.RequestException as err:
        print(f"❌ Сетевой сбой при отправке уведомления {habit_id}: {err}")
        return False

