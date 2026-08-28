from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя в админке с хэшированием пароля."""
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    """Форма для редактирования пользователя в админке."""
    class Meta:
        model = CustomUser
        fields = ("email", "is_active", "is_staff", "is_superuser")


