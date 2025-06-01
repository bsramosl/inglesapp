from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from apps.core.models.models import MultiAppToken
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.core.services.token_service import TokenService

@method_decorator(login_required(login_url='login'), name='dispatch')
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inicio'
        return context


@csrf_exempt
def login_view(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not username or not password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Usuario y contraseña son requeridos'
                }, status=400)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)

                # Crear o actualizar token único
                token = TokenService.get_or_create_token(user)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    url_redirect = '/'
                    return JsonResponse({
                        'status': 'success',
                        'token': token.key,
                        'expires': token.expires.isoformat(),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email
                        },
                        'url_redirect':url_redirect
                    })
                else:
                    return redirect('home')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Usuario o contraseña incorrectos'
                    }, status=401)
                else:
                    return render(request, 'core/login.html', {
                        'error': 'Usuario o contraseña incorrectos',
                        'username': username
                    })

        return render(request, 'core/login.html')
    except Exception as ex:
        return JsonResponse({'status':False, 'message': str(ex)}, status=400)

@login_required
def logout_view(request):
    token_key = request.GET.get('token') or request.POST.get('token')
    if token_key:
        MultiAppToken.objects.filter(key=token_key).update(is_active=False)

    auth_logout(request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('login')