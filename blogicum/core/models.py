"""Абстрактные модели приложения."""

from django.db import models


class CreatedAtModel(models.Model):
    """
    Абстрактная модель с датой создания записи.

    Используется как базовый класс для моделей,
    которым необходимо хранить дату создания объекта.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        """Настройки абстрактной модели."""

        abstract = True


class PublishedModel(CreatedAtModel):
    """
    Абстрактная модель с флагом публикации.

    Используется как базовый класс для моделей,
    которые могут быть опубликованы или скрыты.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    class Meta:
        """Настройки абстрактной модели."""

        abstract = True
