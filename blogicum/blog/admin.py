from django.contrib import admin

from .models import Category, Comment, Location, Post


admin.site.empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    """Inline-редактирование публикаций в категории."""

    model = Post
    fields = (
        'title',
        'is_published',
        'pub_date',
    )
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Администрирование категорий."""

    inlines = [
        PostInline,
    ]
    list_display = (
        'title',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'title',
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Администрирование публикаций блога."""

    list_display = (
        'title',
        'author',
        'category',
        'location',
        'is_published',
        'pub_date',
        'created_at',
    )

    list_editable = (
        'is_published',
        'category',
        'location',
        'pub_date',
    )

    list_display_links = (
        'title',
    )

    search_fields = (
        'title',
    )

    list_filter = ('is_published',
                   'category',
                   'location',
                   'pub_date',
                   'author',
                   )

    fields = ('title',
              'text',
              'author',
              'category',
              'location',
              'is_published',
              'pub_date',
              'image',
              )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Администрирование локаций."""

    readonly_fields = (
        'created_at',
    )
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Администрирование комментариев."""

    readonly_fields = (
        'created_at',
    )
    list_display = (
        'text',
        'post',
        'created_at',
        'is_published',
        'author',
    )
    list_filter = (
        'is_published',
        'post',
        'author',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'text',
        'author__username',
    )
