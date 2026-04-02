from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


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
