from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import CustomUser


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate_password(self, value):
        """Проверка введенного пароля."""
        try:
            # Используем стандартные валидаторы из settings.py (длина, символы и т.д.)
            validate_password(value)
            return value
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

    def create(self, validated_data):
        """Хешируем пароль при сохранении пользователя."""
        return CustomUser.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователей."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:

            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError("Неверный email или пароль")

        else:
            raise serializers.ValidationError("Отсутствует email или пароль")

        attrs['user'] = user # Сохраняем пользователя внутри словаря
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования профиля пользователя."""

    class Meta:
        model = CustomUser
        fields = ["email",]


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка пользователей."""

    class Meta:
        model = CustomUser
        fields = ["id", "email", "is_active", "date_joined"]
        # Защищаем поля от редактирования
        read_only_fields = ["id", "email", "is_active", "date_joined"]














# class ProfileSerializer(serializers.Serializer):
#     """Класс проверки коммерческого стажа пользователя."""
#
#     birth_date = serializers.DateField(required=True)
#     experience_start = serializers.DateField(required=True)
#
#     def validate(self, attrs):
#         birth_date = attrs['birth_date']
#         experience_start = attrs['experience_start']
#
#         if (experience_start - birth_date).days < 18 * 365:
#             raise serializers.ValidationError({"experience_start": "Опыт не мог начаться до вашего совершеннолетия."})
#         return attrs
#
#
# class PhoneRegisterSerializer(serializers.ModelSerializer):
#     """Класс сериализации для регистрации пользователей по номеру телефона."""
#
#     class Meta:
#         model = CustomUser
#         fields = ['phone_number', 'password']
#
#     def validate_phone_number(self, value):
#         pattern = r'^\+7\d{10}$'
#         if not re.match(pattern, value):
#             raise serializers.ValidationError("Некорректный формат номера телефона.")
#         return value
#
#     def create(self, validated_data):
#         return CustomUser.objects.create_user(**validated_data)
#
#
# class CorporateRegisterSerializer(serializers.ModelSerializer):
#     """Класс сериализации для регистрации корпоративных пользователей."""
#
#     password = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'password']
#
#     def to_internal_value(self, data):
#         mutable_data = data.copy() if hasattr(data, 'copy') else data
#         mutable_data['email'] = mutable_data['email'].lower()
#         return super().to_internal_value(mutable_data)
#
#     def validate_email(self, value):
#         prohibited_domains = ['gmail.com', 'mail.ru', 'gmail.com']
#         try:
#             domain = value.split("@")[1]
#         except IndexError:
#             raise serializers.ValidationError("Некорректный формат email.")
#
#         if domain in prohibited_domains:
#             raise serializers.ValidationError("Регистрация через публичные почтовые сервисы запрещена.")
#         return value
#
#     def create(self, validated_data):
#         return CustomUser.objects.create_user(**validated_data)
#
#
#
#
# class UserProfileSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = UserProfile
#         fields = ['telegram', 'bio']
#
#
# class UserWithProfileSerializer(serializers.ModelSerializer):
#
#     profile = UserProfileSerializer()
#     password = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'profile']
#
#     def create(self, validate_data):
#
#         profile_data = validate_data.pop('profile')
#
#         user = CustomUser.objects.create_user(**validate_data)
#
#         UserProfile.objects.create(user=user, **profile_data)
#
#         return user
#
#
# class UserDeviceSerializer(serializers.ModelSerializer):
#
#     device_name = serializers.CharField()
#     phone_number = serializers.CharField()
#
#     class Meta:
#         model = UserDevice
#         fields = ['device_name', 'phone_number']
#
# class UserWithDevicesSerializer(serializers.ModelSerializer):
#
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(write_only=True, required=True)
#     devices = UserDeviceSerializer(many=True)
#
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'password', 'devices']
#
#     def create(self, validate_data):
#
#         devices = validate_data.pop('devices')
#
#         user = CustomUser.objects.create_user(**validate_data)
#
#         for device in devices:
#             UserDevice.objects.create(user=user, **device)
#
#         return user
#
