from django import forms
from django.contrib.auth import get_user_model

from .models import Category, Comment, Location, Post


User = get_user_model()


class EditProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля.

    Модель:
        User

    Доступные для редактирования поля:
        логин, имя, фамилия, адрес электронной почты
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'email': forms.EmailInput(),
        }


class PostForm(forms.ModelForm):
    """
    Форма создания и редактирования поста.

    Модель:
        Post

    Поля:
        заголовок, текст, фото, дата публикации
    """

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'category', 'location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True)
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True)


class CommentForm(forms.ModelForm):
    """
    Форма создания и редактирования комментария.

    Модель:
        Comment

    Поля:
        текст
    """

    class Meta:
        model = Comment
        fields = ('text', )
