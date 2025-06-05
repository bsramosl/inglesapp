from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.conf import settings
from core.models import MultiAppToken
from .services import AuthService
from core.services.user_services import UserService
from django.core.cache import caches
cache = caches['default']


class HybridLoginView(TemplateView):
    template_name = 'users/login.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip_address = AuthService.get_client_ip(request)

        if AuthService.is_login_blocked(username, ip_address):
            return self.render_error(request, 'Demasiados intentos. Espere 15 minutos.', status=429)

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            token = AuthService.record_successful_login(user, ip_address)
            auth_login(request, user)
            return self.handle_success_response(request, user, token)

        AuthService.record_failed_login(username, ip_address)
        return self.render_error(request, 'Credenciales inválidas', status=401)

    def handle_success_response(self, request, user, token):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            user_profile = UserService.get_user_profile(user)
            request.session['user_profile'] = user_profile
            return JsonResponse({
                'status': 'success',
                'token': token.key,
                'expires': token.expires.isoformat(),
                'session_id': request.session.session_key,
                'url_redirect': settings.LOGIN_REDIRECT_URL
            })
        return redirect(request.POST.get('next', settings.LOGIN_REDIRECT_URL))

    def render_error(self, request, message, status=400):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': message}, status=status)
        return render(request, self.template_name, {'error': message})


class HybridLogoutView(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        token_key = request.POST.get('token') or request.GET.get('token')
        if token_key:
            MultiAppToken.objects.filter(key=token_key).update(is_active=False)
            cache.delete_many([
                f"token_validation:{token_key}",
                f"user_tokens:{request.user.id}:default"
            ])

        if request.user.is_authenticated:
            AuthService.logout_user(request.user.id)
            auth_logout(request)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect(settings.LOGOUT_REDIRECT_URL)


class HomeView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sessions'] = AuthService.get_active_sessions(self.request.user.id)
        return context