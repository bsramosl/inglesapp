from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
class ModelBase(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation")
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True, verbose_name="Date modification")
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
        if not user:
            user_id = getattr(settings, 'ADMINISTRATOR_ID', None)
            if user_id:
                user = get_user_model().objects.filter(pk=user_id).first()
        if not self.pk:
            self.created_by = user
        self.updated_by = user
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def hard_delete(self):
        super().delete()

    @classmethod
    def active_objects(cls):
        return cls.objects.filter(is_active=True)

    def __str__(self):
        return f"{self.__class__.__name__} #{self.pk}"

    @property
    def audit_info(self):

        return {
            'created_by': getattr(self.created_by, 'username', None),
            'created_at': self.created_at,
            'updated_by': getattr(self.updated_by, 'username', None),
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }
