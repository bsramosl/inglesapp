import logging
from django.core.cache import caches
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model, authenticate

from app.models import Person, MultiAppToken, LoginAttempt

logger = logging.getLogger(__name__)
cache = caches['default']
User = get_user_model()

class AuthService:
    """Servicio completo de autenticación y gestión de sesiones"""

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

    @staticmethod
    def is_login_blocked(username, ip_address):
        user_key = f"login_attempts:user:{username}"
        ip_key = f"login_attempts:ip:{ip_address}"
        return cache.get(user_key, 0) >= settings.MAX_LOGIN_ATTEMPTS or cache.get(ip_key, 0) >= settings.MAX_LOGIN_ATTEMPTS

    @staticmethod
    def record_failed_login(username, ip_address):
        user_key = f"login_attempts:user:{username}"
        ip_key = f"login_attempts:ip:{ip_address}"
        for key in [user_key, ip_key]:
            if not cache.get(key):
                cache.set(key, 0, timeout=settings.LOGIN_ATTEMPTS_TIMEOUT)
            cache.incr(key)
            cache.expire(key, settings.LOGIN_ATTEMPTS_TIMEOUT)
        LoginAttempt.objects.create(username=username, ip_address=ip_address, status=LoginAttempt.Status.FAILED)

    @staticmethod
    def generate_app_token(user, app_name=settings.TITLE_SYSTEM, action_type=1):
        MultiAppToken.objects.filter(user=user, app_name=app_name, is_active=True).update(is_active=False)
        token = MultiAppToken.objects.create(
            user=user,
            app_name=app_name,
            action_type=action_type,
            expires=timezone.now() + timedelta(days=settings.TOKEN_DEFAULT_EXPIRY_DAYS)
        )
        cache.set(f"user_tokens:{user.id}:{app_name}", token.key, timeout=settings.TOKEN_DEFAULT_EXPIRY_DAYS*24*60*60)
        return token

    @staticmethod
    def record_successful_login(user, ip_address, app_name=settings.TITLE_SYSTEM):
        AuthService.record_login_success(user, ip_address)
        token = AuthService.generate_app_token(user, app_name)
        session_data = {
            'user_id': user.id,
            'ip': ip_address,
            'login_time': timezone.now().isoformat(),
            'user_agent': None,
            'active_tokens': [token.key],
            'current_app': app_name
        }
        cache.set(f"user_session:{user.id}", session_data, timeout=settings.SESSION_COOKIE_AGE)
        return token

    @staticmethod
    def validate_token(token_key):
        cached_user_id = cache.get(f"token_validation:{token_key}")
        if cached_user_id:
            return User.objects.get(id=cached_user_id)
        try:
            token = MultiAppToken.objects.get(key=token_key)
            if token.is_valid():
                cache.set(f"token_validation:{token.key}", token.user.id, timeout=300)
                return token.user
        except MultiAppToken.DoesNotExist:
            pass
        return None

    @staticmethod
    def validate_session(request):
        if not request.user.is_authenticated:
            return False
        session_data = cache.get(f"user_session:{request.user.id}")
        if not session_data:
            return False
        if settings.VALIDATE_SESSION_IP and session_data.get('ip') != AuthService.get_client_ip(request):
            logger.warning(f"IP mismatch for user {request.user.id}")
            return False
        session_data['user_agent'] = request.META.get('HTTP_USER_AGENT')
        cache.set(f"user_session:{request.user.id}", session_data, timeout=settings.SESSION_COOKIE_AGE)
        return True

    def validate_user_credentials(username, password, ip_address):
        username = username
        user = authenticate(username=username, password=password)

        if Person.objects.filter(user__username=username,status=True).exists() and user is None:
            raise NameError("Inicio de Sesión fallido, credenciales incorrectas")

        if user is None:
            raise NameError("Inicio de Sesión fallido, credenciales incorrectas")

        if not user.is_active:
            raise NameError("Inicio de Sesión fallido, usuario no activo")

        if not Person.objects.filter(user=user,status=True).exists():
            raise NameError("Inicio de Sesión fallido, no existe el usuario")

        persona = Person.objects.filter(user=user,status=True).first()

        if not persona.my_profiles():
            raise NameError("Inicio de Sesión fallido, no existe perfiles asignados")

        token = AuthService.record_successful_login(user, ip_address)
        return user, persona, token

    @staticmethod
    def record_login_success(user, ip_address):
        user_key = f"login_attempts:user:{user.username}"
        ip_key = f"login_attempts:ip:{ip_address}"
        # Reinicia los contadores de intentos fallidos
        cache.delete(user_key)
        cache.delete(ip_key)
        # Registra el intento exitoso
        LoginAttempt.objects.create(
            username=user.username,
            ip_address=ip_address,
            status=LoginAttempt.Status.SUCCESS
        )

    @staticmethod
    def get_active_sessions(user_id):
        session_data = cache.get(f"user_session:{user_id}")
        if session_data:
            return session_data
        return None

    @staticmethod
    def logout_user(user_id, session_only=False):
        cache.delete(f"user_session:{user_id}")
        if not session_only:
            MultiAppToken.objects.filter(user_id=user_id, is_active=True).update(is_active=False)
            for token in MultiAppToken.objects.filter(user_id=user_id):
                cache.delete(f"token_validation:{token.key}")
                cache.delete(f"user_tokens:{user_id}:{token.app_name}")
        return True

