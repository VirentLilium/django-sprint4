"""Миксины для представлений приложения blog."""

from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from blog.constants import POSTS_ON_THE_PAGE
from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post
from blog.utils import (
    annotate_comments,
    filter_published,
    optimize_queryset,
    order_by_pub_date,
)


class OnlyAuthorRedirectMixin(UserPassesTestMixin):
    """Проверяет авторство объекта и перенаправляет пользователя без прав."""

    def test_func(self) -> bool:
        """
        Проверяет, является ли текущий пользователь автором объекта.

        :return: True, если пользователь является автором объекта.
        """
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        """
        Перенаправляет пользователя при отсутствии прав.

        :return: HTTP-редирект на страницу, заданную во view.
        """
        return redirect(self.get_redirect_url())

    def get_redirect_url(self) -> str:
        """
        Возвращает URL для перенаправления пользователя.

        Метод должен быть переопределён во view.

        :return: URL для перенаправления.
        :raises NotImplementedError: Если метод не переопределён.
        """
        raise NotImplementedError(
            'Определите get_redirect_url() во view.'
        )


class PaginatedPostsMixin:
    """Добавляет пагинацию к спискам публикаций."""

    model = Post
    paginate_by = POSTS_ON_THE_PAGE


class AssignAuthorMixin:
    """Назначает текущего пользователя автором объекта."""

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """
        Сохраняет текущего пользователя как автора объекта формы.

        :param form: Валидная форма с данными объекта.
        :return: HTTP-ответ после успешной обработки формы.
        """
        form.instance.author = self.request.user
        return super().form_valid(form)


class AssignPostMixin:
    """Назначает публикацию комментарию перед сохранением формы."""

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """
        Сохраняет публикацию в объект комментария.

        :param form: Валидная форма комментария.
        :return: HTTP-ответ после успешной обработки формы.
        """
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class PublishedPostsMixin:
    """Формирует queryset опубликованных публикаций."""

    def get_queryset(self) -> QuerySet[Post]:
        """
        Возвращает опубликованные публикации с оптимизированными запросами.

        :return: QuerySet опубликованных публикаций.
        """
        queryset = Post.objects.all()
        queryset = filter_published(queryset)
        queryset = optimize_queryset(queryset)
        queryset = annotate_comments(queryset)
        return order_by_pub_date(queryset)


class PostPKMixin:
    """Задаёт имя URL-параметра с идентификатором публикации."""

    pk_url_kwarg = 'post_id'


class PostTemplateMixin:
    """Задаёт модель и шаблон для представлений публикаций."""

    model = Post
    template_name = 'blog/create.html'


class PostFormMixin(PostTemplateMixin):
    """Задаёт форму для создания и редактирования публикаций."""

    form_class = PostForm


class CommentModelMixin:
    """Задаёт модель комментария."""

    model = Comment


class CommentFormMixin(CommentModelMixin):
    """Задаёт форму для создания и редактирования комментариев."""

    form_class = CommentForm


class CommentTemplateMixin(CommentModelMixin):
    """Задаёт шаблон и URL-параметр для представлений комментариев."""

    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class ContextObjectMixin:
    """Добавляет объект в контекст шаблона."""

    object_name: str | None = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет объект в контекст по имени object_name.

        :param kwargs: Дополнительные данные контекста.
        :return: Контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        if self.object_name and hasattr(self, self.object_name):
            context[self.object_name] = getattr(self, self.object_name)
        return context
