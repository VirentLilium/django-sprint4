"""Представления приложения blog."""

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.forms import CommentForm, EditProfileForm, PostForm
from blog.mixins import (
    AssignAuthorMixin,
    AssignPostMixin,
    CommentFormMixin,
    CommentTemplateMixin,
    ContextObjectMixin,
    OnlyAuthorRedirectMixin,
    PaginatedPostsMixin,
    PostFormMixin,
    PostPKMixin,
    PostTemplateMixin,
    PublishedPostsMixin,
)
from blog.models import Category, Post
from blog.utils import annotate_comments, optimize_queryset


class PostsListView(PublishedPostsMixin, PaginatedPostsMixin, ListView):
    """Отображает главную страницу со списком публикаций."""

    template_name = 'blog/index.html'


class ProfileView(
    PublishedPostsMixin,
    PaginatedPostsMixin,
    ContextObjectMixin,
    ListView
):
    """Отображает профиль пользователя со списком его публикаций."""

    template_name = 'blog/profile.html'
    object_name = 'profile'

    def get_queryset(self) -> QuerySet[Post]:
        """
        Возвращает публикации пользователя для страницы профиля.

        Для владельца профиля возвращает все публикации.
        Для остальных пользователей возвращает опубликованные публикации.

        :return: QuerySet публикаций пользователя.
        """
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )

        if self.request.user == self.profile:
            queryset = Post.objects.filter(category__isnull=False)
            queryset = optimize_queryset(queryset)
            queryset = annotate_comments(queryset)
        else:
            queryset = super().get_queryset()

        return queryset.filter(author=self.profile).order_by('-pub_date')


class CategoryPostsListView(
    PublishedPostsMixin,
    PaginatedPostsMixin,
    ContextObjectMixin,
    ListView,
):
    """Отображает страницу категории со списком публикаций."""

    template_name = 'blog/category.html'
    object_name = 'category'

    def get_queryset(self) -> QuerySet[Post]:
        """
        Возвращает опубликованные публикации выбранной категории.

        :return: QuerySet публикаций категории.
        """
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

        return super().get_queryset().filter(category=self.category)


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Отображает страницу редактирования профиля пользователя."""

    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset: QuerySet | None = None) -> User:
        """
        Возвращает текущего пользователя для редактирования.

        :param queryset: QuerySet пользователей.
        :return: Текущий пользователь.
        """
        return self.request.user

    def get_success_url(self) -> str:
        """
        Возвращает URL профиля после успешного редактирования.

        :return: URL профиля текущего пользователя.
        """
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostDetailView(PostPKMixin, DetailView):
    """Отображает страницу поста в соответствии с его идентификатором."""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset: QuerySet | None = None) -> Post:
        """
        Возвращает публикацию для детального просмотра.

        Автор может видеть публикацию всегда.
        Остальные пользователи видят только опубликованную публикацию
        с опубликованной категорией и датой публикации не позднее текущей.

        :param queryset: QuerySet публикаций.
        :return: Объект публикации.
        :raises Http404: Если публикация недоступна пользователю.
        """
        queryset = (Post.objects.filter(category__isnull=False))
        queryset = optimize_queryset(queryset)

        post = get_object_or_404(queryset, pk=self.kwargs['post_id'])

        if self.request.user == post.author or (
            post.pub_date <= timezone.now()
            and post.is_published
            and post.category
            and post.category.is_published
        ):
            return post

        raise Http404('Пост не найден')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет форму комментария и комментарии публикации в контекст.

        :param kwargs: Дополнительные данные контекста.
        :return: Контекст страницы публикации.
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['form'] = CommentForm()

        context['comments'] = (
            self.object.comments
            .filter(is_published=True)
            .select_related('author')
        )
        return context


class PostCreateView(
    LoginRequiredMixin,
    PostFormMixin,
    AssignAuthorMixin,
    CreateView,
):
    """Отображает страницу создания публикации."""

    def get_success_url(self) -> str:
        """
        Возвращает URL профиля после создания публикации.

        :return: URL профиля текущего пользователя.
        """
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostUpdateView(
    LoginRequiredMixin,
    PostPKMixin,
    PostFormMixin,
    OnlyAuthorRedirectMixin,
    UpdateView,
):
    """Отображает страницу редактирования публикации."""

    def get_redirect_url(self) -> str:
        """
        Возвращает URL для редиректа пользователя без прав.

        :return: URL страницы публикации.
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )


class PostDeleteView(
    LoginRequiredMixin,
    PostPKMixin,
    PostTemplateMixin,
    OnlyAuthorRedirectMixin,
    DeleteView,
):
    """Отображает страницу удаления публикации."""

    success_url = reverse_lazy('blog:index')

    def get_redirect_url(self) -> str:
        """
        Возвращает URL для редиректа пользователя без прав.

        :return: URL страницы публикации.
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет форму публикации в контекст страницы удаления.

        :param kwargs: Дополнительные данные контекста.
        :return: Контекст страницы удаления публикации.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CommentCreateView(
    LoginRequiredMixin,
    CommentFormMixin,
    AssignAuthorMixin,
    AssignPostMixin,
    CreateView,
):
    """Отображает форму создания комментария."""

    def get_success_url(self) -> str:
        """
        Возвращает URL публикации после создания комментария.

        :return: URL страницы публикации.
        """
        return self.object.post.get_absolute_url()


class CommentUpdateView(
    LoginRequiredMixin,
    CommentFormMixin,
    CommentTemplateMixin,
    OnlyAuthorRedirectMixin,
    UpdateView,
):
    """Отображает страницу редактирования комментария."""

    def get_redirect_url(self) -> str:
        """
        Возвращает URL для редиректа пользователя без прав.

        :return: URL страницы публикации.
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )

    def get_success_url(self) -> str:
        """
        Возвращает URL публикации после редактирования комментария.

        :return: URL страницы публикации.
        """
        return self.get_redirect_url()


class CommentDeleteView(
    LoginRequiredMixin,
    CommentTemplateMixin,
    OnlyAuthorRedirectMixin,
    DeleteView,
):
    """Отображает страницу удаления комментария."""

    def get_redirect_url(self) -> str:
        """
        Возвращает URL для редиректа пользователя без прав.

        :return: URL страницы публикации.
        """
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )

    def get_success_url(self) -> str:
        """
        Возвращает URL публикации после удаления комментария.

        :return: URL страницы публикации.
        """
        return self.get_redirect_url()
