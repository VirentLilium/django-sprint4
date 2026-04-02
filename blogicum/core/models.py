from django.db import models


class CreatedAtModel(models.Model):
    """
    Абстрактная модель с датой создания записи.

    created_at (datetime): Дата и время создания записи.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class PublishedModel(CreatedAtModel):
    """
    Абстрактная модель с флагом публикации.

    is_published (bool): Флаг публикации, True - опубликовано.

    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True
