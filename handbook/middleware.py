from django.conf import settings
from django.utils import translation


class ForceDefaultLanguageMiddleware:
    """
    Middleware для принудительной установки языка по умолчанию.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate(settings.LANGUAGE_CODE)
        response = self.get_response(request)
        return response
