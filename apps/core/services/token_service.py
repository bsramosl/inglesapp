from datetime import datetime
from apps.core.models.models import MultiAppToken


class TokenService:
    @staticmethod
    def get_or_create_token(user, expiration_days=30):
        """Obtiene o crea un token único para el usuario"""
        try:
            token = MultiAppToken.objects.get(user=user)
            if not token.is_valid:
                token.refresh(expiration_days)
            return token
        except MultiAppToken.DoesNotExist:
            return MultiAppToken.objects.create_token(user, expiration_days)

    @staticmethod
    def validate_token(token_key):
        """Valida un token y registra su uso"""
        try:
            token = MultiAppToken.objects.get(key=token_key, is_active=True)
            if token.is_valid:
                token.last_used_at = datetime.now()
                token.save()
                return token
            return None
        except MultiAppToken.DoesNotExist:
            return None

    @staticmethod
    def invalidate_token(user):
        MultiAppToken.objects.filter(user=user).update(is_active=False)