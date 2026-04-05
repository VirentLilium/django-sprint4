from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView,
                                  )

from .forms import CommentForm, EditProfileForm, PostForm
from .mixins import (AssignAuthorMixin, AssignPostMixin, CommentFormMixin,
                     CommentTemplateMixin, ContextObjectMixin,
                     OnlyAuthorRedirectMixin, PaginatedPostsMixin, PostPKMixin,
                     PostTemplateMixin, PostFormMixin, PublishedPostsMixin
                     )
from .models import Category, Post
from .utils import annotate_comments, optimize_queryset


class PostsListView(PublishedPostsMixin, PaginatedPostsMixin, ListView):
    """
    Отображает главную страницу со списком всех постов с пагинацией.

    Использует get_post_objects для фильтрации:
    - дата публикации не позже текущего времени,
    - публикация опубликована,
    - категория опубликована.

    Модель:
        Post
    """

    template_name = 'blog/index.html'


class ProfileView(PublishedPostsMixin, PaginatedPostsMixin,
                  ContextObjectMixin, ListView):
    """
    Страница профиля пользователя со списком его постов с пагинацией.

    Особенности:
    - Для автора отображаются все посты
    (включая отложенные и неопубликованные).
    - Для остальных пользователей отображаются только опубликованные посты
    с опубликованной категорией.

    Модель:
        Post
    """

    template_name = 'blog/profile.html'
    object_name = 'profile'

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.request.user == self.profile:
            queryset = Post.objects.filter(category__isnull=False)
            queryset = optimize_queryset(queryset)
            queryset = annotate_comments(queryset)
        else:
            queryset = super().get_queryset()

        return queryset.filter(author=self.profile).order_by('-pub_date')


class CategoryPostsListView(PublishedPostsMixin, PaginatedPostsMixin,
                            ContextObjectMixin, ListView):
    """
    Страница категории, отображает все посты в категории с пагинацией.

    Фильтры:
    - дата публикации не позже текущего времени,
    - публикация опубликована,
    - категория опубликована.
    - категория определяется по слагу из URL.

    Модель:
        Post
    """

    template_name = 'blog/category.html'
    object_name = 'category'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

        return super().get_queryset().filter(category=self.category)


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Редактирование профиля пользователя.

    Особенности:
    - Только текущий пользователь может редактировать свой профиль.
    - После сохранения редирект на профиль пользователя.

    Модель:
        User

    Форма:
        EditProfileForm
    """

    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username}
                       )


class PostDetailView(PostPKMixin, DetailView):
    """
    Отображает страницу поста в соответствии с его идентификатором.

    Автор поста может видеть его всегда.
    Остальные пользователи только если:
    - дата публикации не позже текущего времени,
    - пост опубликован,
    - категория опубликована.

    Иначе возвращается ошибка 404.

    Модель:
        Post
    """

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
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
        raise Http404("Пост не найден")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        context['comments'] = (self.object.comments
                               .filter(is_published=True)
                               .select_related('author')
                               )
        return context


class PostCreateView(LoginRequiredMixin, PostFormMixin,
                     AssignAuthorMixin, CreateView):
    """
    Создание поста авторизованным пользователем.

    После создание поста редирект на страницу пользователя.

    Модель:
        Post
    """

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username}
                       )


class PostUpdateView(LoginRequiredMixin, PostPKMixin, PostFormMixin,
                     OnlyAuthorRedirectMixin, UpdateView):
    """
    Редактирование поста его автором.

    Если не автор пытается редактировать пост, редирект на страницу поста.

    Модель:
        Post
    """

    def get_redirect_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       )


class PostDeleteView(LoginRequiredMixin, PostPKMixin, PostTemplateMixin,
                     OnlyAuthorRedirectMixin, DeleteView):
    """
    Удаление поста его автором.

    Если не автор пытается удалить пост, редирект на главную страницу.

    Модель:
        Post
    """

    success_url = reverse_lazy('blog:index')

    def get_redirect_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CommentCreateView(LoginRequiredMixin, CommentFormMixin,
                        AssignAuthorMixin, AssignPostMixin, CreateView):
    """
    Создание комментария авторизованным пользователем.

    После создания комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    def get_success_url(self):
        return self.object.post.get_absolute_url()


class CommentUpdateView(LoginRequiredMixin, CommentFormMixin,
                        CommentTemplateMixin, OnlyAuthorRedirectMixin,
                        UpdateView):
    """
    Редактирование комментария его автором.

    После редактирования комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    def get_redirect_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       )

    def get_success_url(self):
        return self.get_redirect_url()


class CommentDeleteView(LoginRequiredMixin, CommentTemplateMixin,
                        OnlyAuthorRedirectMixin, DeleteView):
    """
    Удаление комментария его автором.

    После удаления комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    def get_redirect_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       )

    def get_success_url(self):
        return self.get_redirect_url()
