"""Модуль Celery-задач для приложения Routines."""

from celery import shared_task

from routines.services import current_time_reminders, send_telegram_habit_alert


@shared_task
def send_habit_reminders():
    """Задача-планировщик: находит ID привычек и передает их воркерам."""
    habit_ids = current_time_reminders()

    for habit_id in habit_ids:
        send_single_telegram_notification.delay(habit_id)


@shared_task(
    rate_limit="25/s",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def send_single_telegram_notification(habit_id: int):
    """Задача-исполнитель: физически запускает отправку через функцию."""
    send_telegram_habit_alert(habit_id)
