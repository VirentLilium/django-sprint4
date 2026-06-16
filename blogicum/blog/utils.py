"""Вспомогательные функции для работы с публикациями."""

from django.db.models import Count, QuerySet
from django.utils import timezone

from blog.models import Post


def filter_published(queryset: QuerySet[Post]) -> QuerySet[Post]:
    """
    Возвращает опубликованные публикации.

    Фильтрует публикации по дате публикации,
    статусу публикации и статусу категории.

    :param queryset: Исходный QuerySet публикаций.
    :return: Отфильтрованный QuerySet публикаций.
    """
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )


def optimize_queryset(queryset: QuerySet[Post]) -> QuerySet[Post]:
    """
    Оптимизирует получение связанных объектов.

    Выполняет join для автора, местоположения и категории.

    :param queryset: Исходный QuerySet публикаций.
    :return: Оптимизированный QuerySet публикаций.
    """
    return queryset.select_related('author', 'location', 'category')


def annotate_comments(queryset: QuerySet[Post]) -> QuerySet[Post]:
    """
    Добавляет количество комментариев к публикациям.

    :param queryset: Исходный QuerySet публикаций.
    :return: QuerySet с количеством комментариев.
    """
    return queryset.annotate(comment_count=Count('comments'))


def order_by_pub_date(queryset: QuerySet[Post]) -> QuerySet[Post]:
    """
    Сортирует публикации по дате публикации.

    Публикации отображаются от новых к старым.

    :param queryset: Исходный QuerySet публикаций.
    :return: Отсортированный QuerySet публикаций.
    """
    return queryset.order_by('-pub_date')
