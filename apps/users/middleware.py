from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .services import AuthService
from django.conf import settings
from django.http import JsonResponse

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        public_urls = {
            reverse('users:login'),
            reverse('users:logout'),
        }

        if request.path in public_urls:
            return

        if not request.user.is_authenticated:
            token_key = self._extract_token(request)
            if token_key:
                user = AuthService.validate_token(token_key)
                if user:
                    request.user = user
                    return
            return self._redirect_to_login(request)

        if not AuthService.validate_session(request):
            return self._redirect_to_login(request)

    def _extract_token(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split('Bearer ')[1]
        return request.GET.get('token') or request.POST.get('token')

    def _redirect_to_login(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required',
                'login_url': reverse('users:login')
            }, status=401)
        return redirect(f"{reverse('users:login')}?next={request.path}")