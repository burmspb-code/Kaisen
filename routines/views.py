"""
Модуль представлений (Views) для приложения Routines.

Обеспечивает бизнес-логику и обработку HTTP-запросов для API:
- Создание привычки (Habit) реализовано через generics.CreateAPIView.

"""

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from routines.models import Habit
from routines.paginators import HabitPagination
from routines.serializers import HabitDetailSerializer, HabitListSerializer, HabitSerializer


@extend_schema(
    summary="Создание новой привычки",
    description=(
        "Доступ разрешен зарегистрированным пользователям."
    ),
    responses={
        201: OpenApiResponse(
            description="Привычка успешно создана.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных."
        ),
        401: OpenApiResponse(
            description="Неавторизованный доступ."
        ),
        403: OpenApiResponse(
            description="Доступ запрещен."
        )
    },
    tags=["Привычки"],
)
class HabitCreateAPIView(CreateAPIView):
    """Представление для создания новой привычки."""

    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Используем метод для защиты от кеширования."""
        return Habit.objects.all()

    def perform_create(self, serializer):
        """Внедряем пользователя в новую привычку."""
        serializer.save(user=self.request.user)

@extend_schema(
    summary="Просмотр списка привычек",
    description=(
        "Для просмотра доступны привычки текущего пользователя."
    ),
    responses={
        200: OpenApiResponse(
            response=HabitListSerializer,
            description="Список привычек получен.",
        ),
        401: OpenApiResponse(
            description="Неавторизованный доступ."
        ),
        403: OpenApiResponse(
            description="Доступ запрещен."
        )
    },
    tags=["Привычки"],
)
class HabitListAPIView(ListAPIView):
    """Представление для просмотра списка привычек."""

    serializer_class = HabitListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = HabitPagination

    def get_queryset(self):
        """Список привычек под конкретного пользователя"""
        # ЗАЩИТА ДЛЯ REDOC: если метод вызван роботом-генератором,
        # сразу возвращаем пустой кверисет, не двигаясь дальше по коду.
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()

        user = self.request.user
        # Разрешаем адиминистратору просматривать все привычки
        if user.is_superuser:
            return Habit.objects.all()

        return Habit.objects.filter(user=user)


@extend_schema_view(
    get=extend_schema(
        summary="Получить детали привычки",
        description="Возвращает подробную информацию о конкретной привычке текущего пользователя.",
        tags=["Привычки"],
        responses={
            200: OpenApiResponse(response=HabitDetailSerializer, description="Данные успешно получены."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
            404: OpenApiResponse(description="Привычка не найдена."),
        },
    ),
    put=extend_schema(
        summary="Полное обновление привычки",
        description="Позволяет полностью перезаписать все поля конкретной привычки.",
        tags=["Привычки"],
        responses={
            200: OpenApiResponse(response=HabitDetailSerializer, description="Привычка успешно обновлена."),
            400: OpenApiResponse(description="Ошибка валидации переданных данных."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
            404: OpenApiResponse(description="Привычка не найдена."),
        },
    ),
    patch=extend_schema(
        summary="Частичное обновление привычки",
        description="Позволяет изменить только отдельные поля привычки (например, только локацию).",
        tags=["Привычки"],
        responses={
            200: OpenApiResponse(response=HabitDetailSerializer, description="Данные привычки успешно изменены."),
            400: OpenApiResponse(description="Ошибка валидации переданных данных."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
            404: OpenApiResponse(description="Привычка не найдена."),
        },
    ),
    delete=extend_schema(
        summary="Удаление привычки",
        description="Полностью удаляет привычку текущего пользователя из базы данных (Hard Delete).",
        tags=["Привычки"],
        responses={
            204: OpenApiResponse(description="Привычка успешно удалена (нет содержимого)."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
            404: OpenApiResponse(description="Привычка не найдена."),
        },
    ),
)
class HabitDetailAPIView(RetrieveUpdateDestroyAPIView):
    """Представление для просмотра, редактирования и удаления конкретной привычки."""

    serializer_class = HabitDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Возвращает только те привычки, которые принадлежат текущему пользователю."""
        # ЗАЩИТА ДЛЯ SWAGGER/REDOC: робот-генератор сразу получает пустой кверисет
        # и не падает из-за отсутствия объекта request
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()

        user = self.request.user

        # Разрешаем администратору редактировать и удалять любые привычки
        if user.is_superuser:
            return Habit.objects.all()

        return Habit.objects.filter(user=self.request.user)


@extend_schema(
    summary="Просмотр списка публичных привычек",
    auth=[], # Показывает, что авторизация не нужна
    description=(
        "Просматривать могут любые (неавторизованные) пользователи."
    ),
    responses={
        200: OpenApiResponse(
            response=HabitListSerializer,
            description="Список привычек получен.",
        ),
    },
    tags=["Привычки"],
)
class PublicHabitAPIView(ListAPIView):
    """Представление для просмотра публичных привычек."""

    serializer_class = HabitListSerializer
    permission_classes = (AllowAny,)
    pagination_class = HabitPagination

    def get_queryset(self):
        """Список публичных привычек"""
        # ЗАЩИТА ДЛЯ REDOC: если метод вызван роботом-генератором,
        # сразу возвращаем пустой кверисет, не двигаясь дальше по коду.
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()

        return Habit.objects.filter(is_publicity=True)
