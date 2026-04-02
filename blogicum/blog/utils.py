from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_post_objects():
    """
    Возвращает QuerySet постов с join по заданным полям и фильтрацией.

    - поля для select_related: 'author', 'location', 'category'.
    - фильтры: дата не позднее текущего времени, пост и категория опубликованы.
    - аннотация: comment_count (количество комментариев для каждого поста).
    """
    query_set = (Post.objects
                 .filter(pub_date__lte=timezone.now(),
                         is_published=True,
                         category__is_published=True
                         )
                 .select_related('author', 'location', 'category')
                 .annotate(comment_count=Count('comments'))
                 .order_by('-pub_date')
                 )

    return query_set
