"""Модели приложения blog."""

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from core.models import CreatedAtModel, PublishedModel


User = get_user_model()


class Category(PublishedModel):
    """Модель категории публикаций."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.'
                   ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """
        Возвращает название категории.

        :return: Название категории.
        """
        return self.title

    def get_absolute_url(self) -> str:
        """
        Возвращает URL страницы категории.

        :return: URL страницы категории.
        """
        return reverse('blog:category_posts', args=[self.slug])


class Location(CreatedAtModel):
    """Модель местоположения публикации."""

    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        """
        Возвращает название местоположения.

        :return: Название местоположения.
        """
        return self.name


class Post(PublishedModel):
    """Модель публикации блога."""

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )

    text = models.TextField(
        verbose_name='Текст',
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — '
                   'можно делать отложенные публикации.'
                   ),

    )

    image = models.ImageField(
        upload_to='posts_images',
        blank=True,
        verbose_name='Фото',
        null=True,
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = (
            '-pub_date',
        )

    def __str__(self) -> str:
        """
        Возвращает заголовок публикации.

        :return: Заголовок публикации.
        """
        return self.title

    def get_absolute_url(self) -> str:
        """
        Возвращает URL страницы публикации.

        :return: URL страницы публикации.
        """
        return reverse('blog:post_detail', args=[self.pk])


class Comment(PublishedModel):
    """Модель комментария к публикации."""

    text = models.TextField(
        verbose_name='Текст комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = (
            'created_at',
        )

    def __str__(self) -> str:
        """
        Возвращает строковое представление комментария.

        :return: Информация об авторе и публикации комментария.
        """
        return f'Комментарий от {self.author.username} к "{self.post}"'
