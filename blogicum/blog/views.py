from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)

from .constants import POSTS_ON_THE_PAGE
from .forms import EditProfileForm, PostForm, CommentForm
from .mixins import OnlyAuthorRedirectMixin
from .models import Category, Comment, Post
from .utils import get_post_objects


class PostsListView(ListView):
    """
    Отображает главную страницу со списком всех постов с пагинацией.

    Использует get_post_objects для фильтрации:
    - дата публикации не позже текущего времени,
    - публикация опубликована,
    - категория опубликована.

    Модель:
        Post
    """

    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_post_objects()


class ProfileView(ListView):
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

    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.request.user == self.profile:
            queryset = (Post.objects
                        .filter(category__isnull=False)
                        .select_related('author', 'location', 'category')
                        .annotate(comment_count=Count('comments'))
                        )
        else:
            queryset = get_post_objects()

        return queryset.filter(author=self.profile).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class CategoryPostsListView(ListView):
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

    model = Post
    paginate_by = POSTS_ON_THE_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

        return get_post_objects().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


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
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username}
                            )


class PostDetailView(DetailView):
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
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        queryset = (Post.objects
                    .filter(category__isnull=False)
                    .select_related('author', 'location', 'category')
                    )
        post = get_object_or_404(queryset, pk=self.kwargs['post_id'])

        if self.request.user == post.author:
            return post

        if (
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
        context['comments'] = self.object.comments.all()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Создание поста авторизованным пользователем.

    После создание поста редирект на страницу пользователя.

    Модель:
        Post
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, OnlyAuthorRedirectMixin, UpdateView):
    """
    Редактирование поста его автором.

    Если не автор пытается редактировать пост, редирект на страницу поста.

    Модель:
        Post
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_redirect_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_success_url(self):
        return self.get_redirect_url()


class PostDeleteView(LoginRequiredMixin, OnlyAuthorRedirectMixin, DeleteView):
    """
    Удаление поста его автором.

    Если не автор пытается удалить пост, редирект на главную страницу.

    Модель:
        Post
    """

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_redirect_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Создание комментария авторизованным пользователем.

    После создания комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorRedirectMixin,
                        UpdateView
                        ):
    """
    Редактирование комментария его автором.

    После редактирования комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_redirect_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_success_url(self):
        return self.get_redirect_url()


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorRedirectMixin,
                        DeleteView
                        ):
    """
    Удаление комментария его автором.

    После удаления комментария - редирект на страницу поста.

    Модель:
        Comment
    """

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_redirect_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_success_url(self):
        return self.get_redirect_url()
