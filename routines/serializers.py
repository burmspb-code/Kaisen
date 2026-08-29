"""
Модуль сериализаторов для приложения Routines.
"""

from rest_framework import serializers

from routines.models import Habit


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
