from django.db import models
from django.contrib.auth.models import Group,Permission
from apps.core.models.models import ModelBase


class ModuleCategory(ModelBase):
    name = models.CharField(max_length=100,unique=True)
    icon = models.CharField(max_length=50,blank=True,null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Module Category'
        verbose_name_plural = 'Modules Categories'
        ordering = ['order']

    def __str__(self):
        return self.name

class Module(ModelBase):
    category = models.ForeignKey(ModuleCategory,on_delete=models.CASCADE,verbose_name='Category')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    url = models.CharField(max_length=200,blank=True,null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    needs_permission = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['category__order','order']
        unique_together = ('category','name')

    def __str__(self):
        return self.name

class ModulePermission(ModelBase):
    module = models.ForeignKey(Module,on_delete=models.CASCADE,related_name='permissions')
    code_name = models.SlugField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Module Permission'
        verbose_name_plural = 'Module Permissions'
        unique_together = ('module', 'code_name')

    def __str__(self):
        return f"{self.module.name} | {self.name}"

    @property
    def full_code_name(self):
        return f"{self.module.code_name}.{self.code_name}"

class AccessGroup(ModelBase):
    group = models.OneToOneField(Group,on_delete=models.CASCADE,related_name='access_group')
    modules = models.ManyToManyField(Module,through='AccessGroupModule',related_name='access_groups')
    description = models.TextField(blank=True, null=True)
    is_super_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Access Group'
        verbose_name_plural = 'Access Groups'

    def __str__(self):
        return self.group.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_super_admin:
            # Asignar todos los permisos si es super admin
            self.group.permissions.set(Permission.objects.all())

class AccessGroupModule(ModelBase):
    access_group = models.ForeignKey(AccessGroup,on_delete=models.CASCADE)
    module = models.ForeignKey(Module,on_delete=models.CASCADE)
    permissions = models.ManyToManyField(ModulePermission,blank=True)
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_manage = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Access Group Module'
        verbose_name_plural = 'Access Group Modules'
        unique_together = ('access_group', 'module')

    def __str__(self):
        return f"{self.access_group} - {self.module}"