"""Формы приложения blog."""

from typing import Any

from django import forms
from django.contrib.auth import get_user_model

from blog.models import Category, Comment, Location, Post


User = get_user_model()


class EditProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.

    Позволяет изменять имя пользователя,
    имя, фамилию и адрес электронной почты.
    """

    class Meta:
        """Настройки формы редактирования профиля."""

        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )
        widgets = {
            'email': forms.EmailInput(),
        }


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        """Настройки формы публикации."""

        model = Post
        exclude = (
            'author',
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализирует форму публикации.

        Ограничивает список доступных категорий и локаций
        только опубликованными объектами.

        :param args: Позиционные аргументы формы.
        :param kwargs: Именованные аргументы формы.
        """
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(
            is_published=True,
        )
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True,
        )


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        """Настройки формы комментария."""

        model = Comment
        fields = (
            'text',
        )
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'cols': 50,
                    'rows': 5
                },
            ),
        }
