"""
Модуль сериализаторов для приложения Routines.
"""

from rest_framework import serializers

from routines.models import Habit
from routines.validators import (
    PeriodicityValidator,
    RelatedHabitIsPleasantValidator,
    RewardOrRelatedHabitValidator,
    SignPleasantHabitValidator,
    TimeToCompleteValidator,
)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с привычками."""

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "location",
            "time_at",
            "action",
            "sign_pleasant_habit",
            "related_habit",
            "periodicity",
            "award",
            "time_to_complete",
            "is_publicity",
        )
        read_only_fields = (
            "id",
            "user",
        )


class HabitListSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка привычек."""

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "location",
            "time_at",
            "action",
            "sign_pleasant_habit",
            "related_habit",
            "periodicity",
            "award",
            "time_to_complete",
            "is_publicity",
        )
        read_only_fields = (
            "id",
            "user",
            "location",
            "time_at",
            "action",
            "sign_pleasant_habit",
            "related_habit",
            "periodicity",
            "award",
            "time_to_complete",
            "is_publicity",
        )

class HabitDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования и удаления привычки."""

    def __init__(self, *args, **kwargs):
        # Запускаем стандартную инициализацию родительского класса
        super().__init__(*args, **kwargs)

        # Достаем объект запроса и пользователя из контекста сериализатора
        request = self.context.get("request")
        if request and request.user:
            user = request.user

            # Если пользователь — администратор, расширяем права
            if user.is_superuser:
                # Разрешаем админу менять поле 'user' (перепривязывать привычку к другому человеку)
                # Поле 'id' оставляем read_only, так как первичный ключ базы данных менять нельзя
                self.Meta.read_only_fields = ("id",)

                # Отключаем для администратора жесткие бизнес-валидаторы атомных привычек,
                # чтобы он мог вручную исправить любую запись в базе при необходимости
                self.validators = []

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "location",
            "time_at",
            "action",
            "sign_pleasant_habit",
            "related_habit",
            "periodicity",
            "award",
            "time_to_complete",
            "is_publicity",
        )
        read_only_fields = (
            "id",
            "user",
        )

        # Подключаем кастомные валидаторы
        validators = (
            RewardOrRelatedHabitValidator(),
            TimeToCompleteValidator(),
            RelatedHabitIsPleasantValidator(),
            SignPleasantHabitValidator(),
            PeriodicityValidator(),
        )
