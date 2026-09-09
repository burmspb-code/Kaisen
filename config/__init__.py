"""Инициализация пакета конфигурации проекта Kaisen."""

from .celery import celery as celery_app

__all__ = ("celery_app",)
