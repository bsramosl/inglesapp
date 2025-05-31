from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ModelBase(models.Model):
    """
     Modelo abstracto base con:
     - Auditoría de creación/modificación
     - Eliminación lógica
     - Manejo automático de usuarios y fechas
     """
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date modification")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='%(class)s_created',on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Created by")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_updated',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modification by"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at']), models.Index(fields=['is_active']),]

    def save(self, *args, **kwargs):
        from django.contrib.auth.models import AnonymousUser
        user = kwargs.pop('user', None)
        request = kwargs.pop('request', None)

        if request and hasattr(request, 'user'):
            user = request.user if not isinstance(request.user, AnonymousUser) else None

        # Asignar usuario administrador por defecto si no hay usuario
        if not user:
            user_id = getattr(settings, 'ADMINISTRATOR_ID', None)
            if user_id:
                user = get_user_model().objects.filter(pk=user_id).first()

        # Manejo de campos de auditoría
        if not self.pk:
            self.created_by = user
        self.updated_by = user

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Sobrescribe delete para implementar eliminación lógica
        """
        self.is_active = False
        self.save(update_fields=['is_active'])

    def hard_delete(self):
        """
        Eliminación real de la base de datos
        """
        super().delete()

    @classmethod
    def active_objects(cls):
        """
        Manager alternativo para obtener solo objetos activos
        """
        return cls.objects.filter(is_active=True)

    def __str__(self):
        """
        Representación por defecto, puede ser sobrescrita en modelos hijos
        """
        return f"{self.__class__.__name__} #{self.pk}"

    @property
    def audit_info(self):
        """
        Propiedad para obtener información de auditoría
        """
        return {
            'created_by': getattr(self.created_by, 'username', None),
            'created_at': self.created_at,
            'updated_by': getattr(self.updated_by, 'username', None),
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }