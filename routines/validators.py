"""Модуль кастомных валидаторов приложения Routines."""


from datetime import timedelta

from rest_framework import serializers


class RewardOrRelatedHabitValidator:
    """Исключение из модели одновременного указания связанной привычки и вознаграждения."""

    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")
        award = attrs.get("award")

        if related_habit and award:
            raise serializers.ValidationError(
                "Нельзя одновременно указать связанную привычку и вознаграждение. "
                "Выберите что-то одно."
            )


class TimeToCompleteValidator:
    """Проверка на время выполнения."""

    def __call__(self, attrs):
        time_to_complete = attrs.get("time_to_complete")

        if time_to_complete and time_to_complete > timedelta(seconds=120):
            raise serializers.ValidationError(
                "Время на выполнение привычки не может превышать 120 секунд."
            )


class RelatedHabitIsPleasantValidator:
    """Проверка связанной привычки на признак приятной привычки."""

    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")

        if related_habit and not related_habit.sign_pleasant_habit:
            raise serializers.ValidationError(
                "В связанные привычки могут попадать только те привычки, "
                "у которых включен признак приятной привычки (sign_pleasant_habit=True)."
            )


class SignPleasantHabitValidator:
    """Проверка приятной привычки на отсутствие вознаграждения или связанной привычки."""

    def __call__(self, attrs):
        instance = getattr(self, "instance", None) # Безапостное извлечение объекта (для PATCH)
        # ======= Сначала извлекаем данные из запроса, если их нет извлекаем из БД =======
        sign_pleasant_habit = attrs.get("sign_pleasant_habit", getattr(instance, "sign_pleasant_habit", False))
        award = attrs.get("award", getattr(instance, "award", None))
        related_habit = attrs.get("related_habit", getattr(instance, "related_habit", None))
        # =================================================================================

        if sign_pleasant_habit and (award or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )


class PeriodicityValidator:
    """Проверка периодичности привычки."""

    def __call__(self, attrs):
        instance = getattr(self, "instance", None)
        # Извлекаем периодичность из запроса, если нет из БД
        periodicity = attrs.get("periodicity", getattr(instance, "periodicity", None))

        if  periodicity is not None:
            if periodicity < 1 or periodicity >7:
                raise serializers.ValidationError(
                    "Нельзя выполнять привычку реже, чем один раз в неделю."
                )
