from django.http import JsonResponse
from apps.core.models.models import MultiAppToken
from django.utils.deprecation import MiddlewareMixin
from apps.core.services.user_service import (UserService)

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            token_key = request.headers.get('Authorization', '').replace('Token ', '')
            if token_key:
                try:
                    token = MultiAppToken.objects.get(key=token_key)
                    if token.is_valid():
                        request.user = token.user
                    else:
                        return JsonResponse({'error': 'Token expirado o inválido'}, status=401)
                except MultiAppToken.DoesNotExist:
                    return JsonResponse({'error': 'Token no válido'}, status=401)

        return self.get_response(request)


class UserDataMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user_profile = UserService.get_user_profile(request.user)
