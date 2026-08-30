"""
Маршрутизация (URL) приложения Routines.
"""

from django.urls import path

from routines.apps import RoutinesConfig
from routines.views import HabitCreateAPIView, HabitDetailAPIView, HabitListAPIView, PublicHabitAPIView

app_name = RoutinesConfig.name

urlpatterns = [
    # Общий список всех публичных привычек
    path(
        "routines/public/",
        PublicHabitAPIView.as_view(),
        name="routines-public",
    ),
    # Список привычек
    path(
        "routines/",
        HabitListAPIView.as_view(),
        name="routines-list",
    ),
    # Создание новой привычки
    path(
        "routines/create/",
        HabitCreateAPIView.as_view(),
        name="habit-create",
    ),
    # Редактирование/удаление привычки
    path(
        "routines/<int:pk>/",
        HabitDetailAPIView.as_view(),
        name="habit-detail",
    ),
]
