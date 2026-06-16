"""Обработчики ошибок приложения pages."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    """
    Отображает страницу ошибки CSRF.

    :param request: Объект HTTP-запроса.
    :param reason: Причина возникновения ошибки CSRF.
    :return: HTTP-ответ со страницей ошибки 403.
    """
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Отображает страницу ошибки 404.

    :param request: Объект HTTP-запроса.
    :param exception: Исключение, вызвавшее ошибку.
    :return: HTTP-ответ со страницей ошибки 404.
    """
    return render(request, 'pages/404.html', status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """
    Отображает страницу ошибки 500.

    :param request: Объект HTTP-запроса.
    :return: HTTP-ответ со страницей ошибки 500.
    """
    return render(request, 'pages/500.html', status=500)
