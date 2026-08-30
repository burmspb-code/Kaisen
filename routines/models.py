from django.db import models

from users.models import CustomUser


class Habit(models.Model):
    """Класс привычки."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, к которому привязана привычка",
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Место",
        help_text="Место, где должна выполняться привычка",
    )
    time_at = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Время",
        help_text="Время, когда нужно выполнить привычку",
    )
    action = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Действие",
        help_text="Действие, которое нужно выполнить",
    )
    sign_pleasant_habit = models.BooleanField(
        default=False,
        verbose_name="Признак приятности",
        help_text="Укажите: либо True, либо False",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Связанная привычка",
        help_text="Связанная привычка",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Укажите количество дней (по умолчанию 1 день)",
    )
    award = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение",
    )
    time_to_complete = models.DurationField(
        blank=True,
        null=True,
        verbose_name="Время на выполнение",
        help_text="Укажите в формате ЧЧ:ММ:СС",
    )
    is_publicity = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Укажите: либо True, либо False",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"{self.user} - {self.action}"
