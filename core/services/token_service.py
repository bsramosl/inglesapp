from django.core.cache import caches
from django.utils import timezone
from datetime import timedelta
from ..models import MultiAppToken
import secrets

cache = caches['default']


class TokenService:
    @staticmethod
    def get_or_create_token(user, app_name='default', action_type=1):
        # Verificar en cache primero
        cache_key = f"user_token:{user.id}:{app_name}"
        cached_token = cache.get(cache_key)

        if cached_token and MultiAppToken.objects.filter(key=cached_token, is_active=True).exists():
            return MultiAppToken.objects.get(key=cached_token)

        # Eliminar tokens antiguos del mismo tipo
        MultiAppToken.objects.filter(user=user, app_name=app_name).update(is_active=False)

        # Crear nuevo token
        token = MultiAppToken.objects.create(
            user=user,
            app_name=app_name,
            action_type=action_type,
            expires=timezone.now() + timedelta(days=30)
        )

        # Actualizar cache
        cache.set(cache_key, token.key, timeout=30 * 24 * 60 * 60)  # 30 días

        return token

    @staticmethod
    def validate_token(token_key):
        # Verificar en cache primero
        cache_key = f"token_validation:{token_key}"
        cached_validation = cache.get(cache_key)

        if cached_validation is not None:
            return cached_validation

        try:
            token = MultiAppToken.objects.get(key=token_key)
            is_valid = token.is_active and (token.expires is None or token.expires > timezone.now())
        except MultiAppToken.DoesNotExist:
            is_valid = False

        # Cachear resultado por 5 minutos
        cache.set(cache_key, is_valid, timeout=300)
        return is_valid

    @staticmethod
    def get_user_from_token(token_key):
        cache_key = f"token_user:{token_key}"
        user_id = cache.get(cache_key)

        if user_id:
            return user_id

        try:
            token = MultiAppToken.objects.get(key=token_key)
            if token.is_valid():
                cache.set(cache_key, token.user.id, timeout=3600)
                return token.user.id
        except MultiAppToken.DoesNotExist:
            pass

        return None