from django.db import models

from apps.core.models import Module
from apps.core.models.models import  ModelBase
from django.contrib.auth.models import User, Group


class People(ModelBase):
    names =  models.CharField(default='', max_length=100, verbose_name=u"Names")
    surname1 =  models.CharField(default='', max_length=50, verbose_name=u"1er Surname")
    surname2 = models.CharField(default='',max_length=50,verbose_name=u"2do Surname")
    email = models.CharField(default='', max_length=200, verbose_name=u"Persona email")
    phone = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    access_groups = models.ManyToManyField('core.AccessGroup',blank=True,related_name='people' )

    class Meta:
        verbose_name = 'People'

    def get_user_permissions(self):
        if not self.user:
            return set()

        permissions = set()
        # Permisos directos del usuario
        permissions.update(self.user.user_permissions.all())

        # Permisos de los grupos de acceso
        for group in self.access_groups.all():
            permissions.update(group.group.permissions.all())
            for agm in group.accessgroupmodule_set.all():
                permissions.update(agm.permissions.all())

        return {f"{perm.content_type.app_label}.{perm.codename}" for perm in permissions}

    def has_module_access(self, module_code_name):
        if not self.user:
            return False

        # Superusuarios tienen acceso a todo
        if self.user.is_superuser:
            return True

        try:
            module = Module.objects.get(id=module_code_name)
        except Module.DoesNotExist:
            return False

        # Si el módulo no requiere permiso
        if not module.needs_permission:
            return True

        # Verificar en los grupos de acceso
        for ag in self.access_groups.all():
            if ag.is_super_admin:
                return True
            if ag.modules.filter(id=module.id).exists():
                return True

        return False

    def capitalizar_nombre(self, text):
        return ' '.join([word.capitalize() for word in text.strip().split()])

    def name_minus(self):
        try:
            return self.capitalizar_nombre(self.names)
        except Exception:
            return self.names.capitalize()

    def full_name(self):
        return f'{self.names} {self.surname1} {self.surname2}'

    def reverse_full_name(self):
        return f'{self.surname1} {self.surname2} {self.names}'

    def nombre_completo_minus(self):
        try:
            nombre = self.name_minus()
            apellido1 = self.capitalizar_nombre(self.surname1)
            apellido2 = self.capitalizar_nombre(self.surname2)
            return f'{nombre} {apellido1} {apellido2}'
        except Exception:
            return f'{self.names} {self.surname1} {self.surname2}'