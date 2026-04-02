from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from .constants import POSTS_ON_THE_PAGE
from .forms import CommentForm, PostForm
from .models import Comment, Post
from .utils import get_post_objects


class OnlyAuthorRedirectMixin(UserPassesTestMixin):
    """Проверяет авторство и редиректит, если нет прав."""

    def test_func(self):
        """Проверяет авторство."""
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        """Редирект, если обращается не автор."""
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        """Редирект в случае успешного выполнения.

        Должен быть переопределён во view.
        """
        raise NotImplementedError(
            "Определите get_redirect_url() во view"
        )


class PaginatedPostsMixin:
    """Добавляет пагинацию ко всем ListView с постами."""

    model = Post
    paginate_by = POSTS_ON_THE_PAGE


class AssignAuthorMixin:
    """Назначает текущего пользователя автором перед сохранением формы."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AssignPostMixin:
    """Назначает пост для комментария перед сохранением формы."""

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class PublishedPostsMixin:
    """Базовый queryset с фильтрацией по опубликованным постам и категориям."""

    def get_queryset(self):
        return get_post_objects()


class PostPKMixin:
    """Задаёт pk_url_kwarg для всех views с единственным постом."""

    pk_url_kwarg = 'post_id'


class PostTemplateMixin:
    """Задаёт модель поста и шаблон по умолчанию."""

    model = Post
    template_name = 'blog/create.html'


class PostFormMixin(PostTemplateMixin):
    """Задаёт форму поста."""

    form_class = PostForm


class CommentModelMixin:
    """Задаёт модель комментария."""

    model = Comment


class CommentFormMixin(CommentModelMixin):
    """Задаёт форму комментария."""

    form_class = CommentForm


class CommentTemplateMixin(CommentModelMixin):
    """Задаёт шаблон и pk_url_kwarg для Update/Delete комментария."""

    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class ContextObjectMixin:
    """Добавляет объект в контекст под именем object_name."""

    object_name: str | None = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_name and hasattr(self, self.object_name):
            context[self.object_name] = getattr(self, self.object_name)
        return context
