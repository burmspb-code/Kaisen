from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, inline_serializer
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from users.serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, UserListSerializer
from users.serializers import UserRegisterSuccessResponseSerializer


@extend_schema(
    summary="Регистрация нового пользователя",
    description=(
        "Создает новый аккаунт пользователя в системе. "
        "Формирует токен для нового пользователя. "
        "Доступ разрешен незарегистрированным пользователям без авторизации."
    ),
    responses={
        201: OpenApiResponse(
            response=UserRegisterSuccessResponseSerializer,  # Чисто и красиво
            description="Пользователь успешно зарегистрирован.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных."
        ),
    },
    tags=["Пользователи"],
)
class UserRegisterAPIView(CreateAPIView):
    """Представление для регистрации пользователей."""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Сохраняем пользователя в базу данных
        user = serializer.save()

        # ГЕНЕРИРУЕМ ТОКЕН: Создаем токен в БД для нового пользователя
        token, created = Token.objects.get_or_create(user=user)

        # Формируем красивый ответ для фронтенда
        return Response(
            {
                "user": {
                    "email": user.email
                },
                "token": token.key,  # Отправляем ключ, который фронтенд сохранит у себя
                "message": "Пользователь успешно зарегистрирован."
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Аутентификация пользователя",
    description=(
        "Возвращает ответ со статусом 200 OK, токен авторизации и email пользователя при успешном входе. "
        "Доступ разрешен незарегистрированным пользователям без авторизации."
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name='UserLoginResponse',
                fields={
                    'message': serializers.CharField(default='Успешный вход'),
                    'token': serializers.CharField(),  # Обязательно добавляем в документацию
                    'email': serializers.EmailField()
                }
            ),
            description="Авторизация прошла успешно.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных (например, неверный формат email)."
        ),
        401: OpenApiResponse(
            description="Неверный email/пароль или аккаунт деактивирован."
        ),
    },
    tags=["Пользователи"],
)
class UserLoginAPIView(APIView):
    """Класс для входа пользователей с выдачей токена."""

    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # ЗАЩИТА ОТ МЯГКОГО УДАЛЕНИЯ: Не пускаем удаленных пользователей
        if not user.is_active:
            return Response(
                {"detail": "Этот аккаунт деактивирован."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ГЕНЕРИРУЕМ ТОКЕН: Создаем или берем существующий токен из базы данных
        token, created = Token.objects.get_or_create(user=user)

        # Возвращаем токен клиенту
        return Response(
            {
                'message': 'Успешный вход',
                'token': token.key,  # Фронтенд сохранит этот ключ и будет использовать дальше
                'email': user.email,
            },
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(
        summary="Получить информацию о пользователе",
        description="Доступно зарегистрированному пользователю для просмотра своей личной информации.",
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Информация успешно получена."),
            401: OpenApiResponse(description="Неавторизованный доступ (отсутствует или неверен токен)."),
        }
    ),
    put=extend_schema(
        summary="Полное обновление информации о пользователе",
        description="Доступно зарегистрированному пользователю для полного изменения своего профиля.",
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Профиль успешно обновлен."),
            400: OpenApiResponse(description="Ошибка валидации переданных данных."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
        }
    ),
    patch=extend_schema(
        summary="Частичное обновление информации о пользователе",
        description="Доступно зарегистрированному пользователю для частичного изменения данных профиля.",
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Данные профиля успешно изменены."),
            400: OpenApiResponse(description="Ошибка валидации переданных данных."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
        }
    ),
    delete=extend_schema(
        summary="Удаление профиля пользователя",
        description="Мягкое удаление профиля текущего авторизованного пользователя (деактивация).",
        responses={
            204: OpenApiResponse(description="Профиль успешно деактивирован (нет содержимого)."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
        }
    ),
)
class UserProfileAPIView(RetrieveUpdateDestroyAPIView):
    """Класс для просмотра, обновления и мягкого удаления профиля пользователя."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        # Вместо удаления из БД — деактивируем аккаунт
        instance.is_active = False
        instance.save()

        # Инвалидируем токен, чтобы с ним больше нельзя было делать запросы
        if hasattr(instance, "auth_token"):
            instance.auth_token.delete()

        # Дополнительно очищаем текущую сессию
        logout(self.request)


@extend_schema(
    summary="Просмотр списка пользователей",
    description="Возвращает список всех активных зарегистрированных пользователей системы. Доступ разрешен только администраторам.",
    responses={
        200: OpenApiResponse(
            response=UserListSerializer,  # Корректно подхватит пагинацию, если она есть
            description="Список пользователей успешно получен.",
        ),
        401: OpenApiResponse(
            description="Неавторизованный доступ (отсутствует или неверен токен)."
        ),
        403: OpenApiResponse(
            description="Доступ запрещен (пользователь не является администратором)."
        ),
    },
    tags=["Пользователи"],
)
class UserListAPIView(ListAPIView):
    """Класс для просмотра списка пользователей."""

    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Фильтруем список, исключая мягко удаленных пользователей
        return CustomUser.objects.filter(is_active=True)


@extend_schema(
    summary="Выход пользователя из системы",
    description="Завершает текущую сессию пользователя и очищает данные авторизации. Доступно только авторизованным пользователям.",
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name='UserLogoutResponse',
                fields={
                    'message': serializers.CharField(default='Вы успешно вышли из системы.')
                }
            ),
            description="Выход из системы выполнен успешно.",
        ),
        401: OpenApiResponse(
            description="Неавторизованный доступ (отсутствует активная сессия или токен)."
        ),
    },
    tags=["Пользователи"],
)
class UserLogoutAPIView(APIView):
    """Класс для выхода пользователя с инвалидацией токена."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Безопасное удаление токена
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()

        logout(request)  # Очищаем сессию

        return Response(
            {"message": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK
        )
