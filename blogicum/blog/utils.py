from django.db.models import Count
from django.utils import timezone


def filter_published(queryset):
    """
    Возвращает QuerySet с фильтрацией:
    - дата не позднее текущего времени, пост и категория опубликованы.
    """
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def optimize_queryset(queryset):
    """
    Возвращает QuerySet с join по полям:
    - 'author', 'location', 'category'.
    """
    return queryset.select_related('author', 'location', 'category')


def annotate_comments(queryset):
    """Подсчитывает количество комментариев для каждого поста."""
    return queryset.annotate(comment_count=Count('comments'))


def order_by_pub_date(queryset):
    """Сортирует QuerySet по дате публикации от новых к старым."""
    return queryset.order_by('-pub_date')
