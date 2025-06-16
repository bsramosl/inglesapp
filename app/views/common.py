from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import caches

from app.models import MultiAppToken
from helpers.decorators import add_data
from services.auth import AuthService

cache = caches['default']

class HybridLoginView(TemplateView):
    template_name = 'users/login.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        ip_address = AuthService.get_client_ip(request)

        if AuthService.is_login_blocked(username, ip_address):
            return self.render_error(request, 'Demasiados intentos. Espere 15 minutos.', status=429)

        try:
            user, persona, token = AuthService.validate_user_credentials(username, password, ip_address)
            auth_login(request, user)
            return self.handle_success_response(request, persona, token)
        except Exception as ex:
            AuthService.record_failed_login(username, ip_address)
            return self.render_error(request, str(ex), status=400)



    def handle_success_response(self, request, person,token):
        try:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                perfiles = person.my_profiles()
                perfilprincipal = person.main_profile()
                request.session.set_expiry(240 * 60)
                request.session['profiles'] = perfiles
                request.session['person'] = person
                request.session['profilemain'] = perfilprincipal
                # request.session['companybranchmain'] = perfilprincipal.profile.my_company_branches()[0]
                url_redirect = request.POST.get('next', '')
                return JsonResponse({'result': 'success','session_id': request.session.session_key,'token': token.key,'expires': token.expires.isoformat(),'url_redirect': url_redirect})
            return self.render_error(request, 'Credenciales inválidas', status=401)
        except Exception as ex:
            return JsonResponse({'result': False,'message': str(ex)})

    def render_error(self, request, message, status=400):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'result': False, 'message': message})
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
        add_data(self.request, context)
        context['active_sessions'] = AuthService.get_active_sessions(self.request.user.id)
        return context