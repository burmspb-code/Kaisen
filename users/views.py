from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from users.serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, UserListSerializer


class UserRegisterAPIView(CreateAPIView):
    """Класс для решистрации пользователей."""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


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

class UserProfileAPIView(RetrieveUpdateAPIView):
    """Класс для просмотра и обновления профиля пользователя."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListAPIView(ListAPIView):
    """Класс для просмотра списка пользователей."""

    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.all()


class UserLogoutAPIView(APIView):
    """Класс для выхода пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request) # Ощищаем сессию

        return Response(
            {"message": "Вы успешно вышли из системы."},
            status=status.HTTP_200_OK
        )


