from drf_spectacular.utils import inline_serializer, extend_schema, extend_schema_view, OpenApiResponse
from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, UserListSerializer


@extend_schema(
    summary="Регистрация нового пользователя",
    description=(
        "Создает новый аккаунт пользователя в системе. "
        "Доступ разрешен незарегистрированным пользователям без авторизации."
    ),
    responses={
        201: OpenApiResponse(
            response=UserRegisterSerializer,
            description="Пользователь успешно зарегистрирован.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных (например, этот email уже зарегистрирован или слабый пароль)."
        ),
    },
    tags=["Пользователи"],
)
class UserRegisterAPIView(CreateAPIView):
    """Представление для регистрации пользователей."""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


@extend_schema(
    summary="Аутентификация пользователя",
    description=(
        "Возвращает ответ со статусом 200 OK и email пользователя при успешном входе. "
        "Доступ разрешен незарегистрированным пользователям без авторизации."
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name='UserLoginResponse',
                fields={
                    'message': serializers.CharField(default='Успешный вход'),
                    'email': serializers.EmailField()
                }
            ),
            description="Авторизация прошла успешно.",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных (например, неверный формат email)."
        ),
        401: OpenApiResponse(
            description="Неверное имя пользователя или пароль."
        ),
    },
    tags=["Пользователи"],
)
class UserLoginAPIView(APIView):
    """Класс для входа пользователей."""

    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        return Response(
            {
                'message': 'Успешный вход',
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
        description="Удаление профиля текущего авторизованного пользователя.",
        responses={
            204: OpenApiResponse(description="Профиль успешно удален (нет содержимого)."),
            401: OpenApiResponse(description="Неавторизованный доступ."),
        }
    ),
)
class UserProfileAPIView(RetrieveUpdateDestroyAPIView):
    """Класс для просмотра и обновления профиля пользователя."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    summary="Просмотр списка пользователей",
    description="Возвращает список всех зарегистрированных пользователей системы. Доступ разрешен только администраторам.",
    responses={
        200: UserListSerializer,  # Указываем сериализатор напрямую, чтобы drf-spectacular правильно построил схему списка/пагинации
        401: OpenApiResponse(description="Неавторизованный доступ (отсутствует или неверен токен)."),
        403: OpenApiResponse(description="Доступ запрещен (пользователь не является администратором)."),
    },
    tags=["Пользователи"],
)
class UserListAPIView(ListAPIView):
    """Класс для просмотра списка пользователей."""

    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.all()


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
    """Класс для выхода пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request) # Ощищаем сессию

        return Response(
            {"message": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK
        )


