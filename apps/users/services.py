import logging
from django.core.cache import caches
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from core.models import MultiAppToken
from core.services.user_services import UserService
from .models import LoginAttempt

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
        cache.incr(user_key)
        cache.incr(ip_key)
        cache.expire(user_key, settings.LOGIN_ATTEMPTS_TIMEOUT)
        cache.expire(ip_key, settings.LOGIN_ATTEMPTS_TIMEOUT)
        LoginAttempt.objects.create(username=username, ip_address=ip_address, status=LoginAttempt.Status.FAILED)

    @staticmethod
    def generate_app_token(user, app_name=settings.TOKEN_DEFAULT_APP_NAME, action_type=1):
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
    def record_successful_login(user, ip_address, app_name=settings.TOKEN_DEFAULT_APP_NAME):
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


def sessiones(request):
    people = request.session['user_profile']
    user_profile = UserService.get_user_profile(people.user)
    request.session['user_profile'] = user_profile
# class UserService:
#     @staticmethod
#     def get_user_profile(people):
#         cache_key = f"user_profile_v2:{people.user.id}"
#         cached_data = cache.get(cache_key)
#
#         if cached_data:
#             return json.loads(cached_data)
#
#         try:
#             # Obtener módulos accesibles con una sola consulta optimizada
#             accessible_modules = Module.objects.filter(
#                 accessgroupmodule__access_group__in=people.access_groups.all(),
#                 accessgroupmodule__can_view=True,
#                 is_active=True,
#                 visible=True
#             ).distinct().select_related('category').prefetch_related('permissions')
#
#             # Construcción optimizada del menú
#             menu_structure = {}
#             for module in accessible_modules:
#                 category_data = menu_structure.setdefault(module.category.name, {
#                     'icon': module.category.icon,
#                     'order': module.category.order,
#                     'modules': []
#                 })
#                 category_data['modules'].append({
#                     'name': module.name,
#                     'icon': module.icon,
#                     'order': module.order,
#                     'url': module.url,
#                     'permissions': [f"{perm.content_type.app_label}.{perm.codename}" for perm in
#                                     module.permissions.all()]
#                 })
#
#             # Ordenamiento más eficiente
#             sorted_menu = {
#                 category: {
#                     'icon': data['icon'],
#                     'modules': sorted(data['modules'], key=lambda x: x['order'])
#                 }
#                 for category, data in sorted(
#                     menu_structure.items(),
#                     key=lambda item: item[1]['order']
#                 )
#             }
#
#             profile_data = {
#                 'id': people.id,
#                 'username': people.user.username,
#                 'email': people.email,
#                 'people': {
#                     'id': people.id,
#                     'full_name': people.full_name(),
#                     'email': people.email
#                 },
#                 'last_login': people.user.last_login.isoformat() if people.user.last_login else None,
#                 'date_joined': people.user.date_joined.isoformat(),
#                 'menu': sorted_menu,
#                 'permissions': list(people.get_user_permissions()),
#             }
#
#             # Cache con compresión y timeout específico
#             cache.set(
#                 cache_key,
#                 json.dumps(profile_data),
#                 timeout=settings.CACHES['default'].get('TIMEOUT', 3600),
#                 version=2  # Versión para manejar cambios de estructura
#             )
#             return profile_data
#         except Exception as e:
#             from django.views.debug import ExceptionReporter
#             reporter = ExceptionReporter(None, e, None)
#             logger.error(f"Error en UserService: {e}\n{reporter.get_traceback_text()}")
#             return {}
#
#
