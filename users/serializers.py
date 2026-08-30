"""
Модуль сериализаторов для приложения управления пользователями (Users).
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from users.models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'tg_chat_id')

    def validate_password(self, value):
        """Проверка введенного пароля."""
        try:
            # Используем стандартные валидаторы из settings.py (длина, символы и т.д.)
            validate_password(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages) from e

    def create(self, validated_data):
        """Хешируем пароль при сохранении пользователя."""
        user = CustomUser.objects.create_user(
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователей."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # DRF гарантирует, что email и password здесь есть благодаря required=True
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Неверный email или пароль")

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования профиля пользователя."""

    class Meta:
        model = CustomUser
        fields = ("email", "tg_chat_id")


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка пользователей."""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "tg_chat_id", "is_active", "date_joined")
        # Защищаем поля от редактирования
        read_only_fields = ("id", "email", "tg_chat_id", "is_active", "date_joined")


class UserNestedSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserRegisterSuccessResponseSerializer(serializers.Serializer):
    user = UserNestedSerializer()
    token = serializers.CharField()
    message = serializers.CharField()
