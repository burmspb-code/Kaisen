"""Модуль кастомных прав пользователей."""

from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    """Разрешение для владельца объекта."""

    def has_object_permission(self, request, view, obj):
        """Проверяет, является ли пользователь владельцем объекта."""
        return obj.user == request.user


