"""Настройки административной панели для управления пользователями."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Панель администратора для управления кастомной моделью пользователя CustomUser.

    Обеспечивает безопасное создание, редактирование и смену паролей для
    кастомных пользователей на базе AbstractBaseUser.
    """

    # Подключаем кастомные формы создания и редактирования пользователей
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    ordering = ("email",)

    # Поля, которые отображаются в таблице списка пользователей
    list_display = (
        "id",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
    )

    list_filter = ("is_staff", "is_superuser", "is_active")
    readonly_fields = ("date_joined", "last_login")
    search_fields = ("email",)

    # Разделяем поля на логические блоки внутри страницы редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Блок полей, которые запрашиваются при СОЗДАНИИ пользователя через кнопку "Add User"
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "password_confirm"), # Поля из вашей CustomUserCreationForm
            },
        ),
    )
