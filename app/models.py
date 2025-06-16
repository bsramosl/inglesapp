import os
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User, Group, Permission
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.crypto import get_random_string
from app.choices import ActionTypeUserToken, Priorities, Types
from helpers.model_base import ModelBase


def person_photo_path(instance, filename):
    return os.path.join('persons', instance.dni, filename)

def learning_content_path(instance, filename):
    return os.path.join('learning_content', str(instance.id), filename)

class MultiAppToken(ModelBase):
    user = models.ForeignKey(User, related_name='tokens', on_delete=models.CASCADE, db_index=True)
    key = models.CharField(max_length=64, primary_key=True)
    expires = models.DateTimeField(blank=True, null=True, db_index=True)
    app_name = models.CharField(max_length=50, db_index=True)
    action_type = models.IntegerField(choices=ActionTypeUserToken.CHOICES, default=1, verbose_name='Tipo de acción',db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)


    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
        ordering = ('user', 'expires',)
        indexes = [
            models.Index(fields=['user', 'expires']),
            models.Index(fields=['expires']),
            models.Index(fields=['app_name']),
        ]

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.expires:
            self.expires = datetime.now() + timedelta(days=30)

        MultiAppToken.objects.filter(user=self.user).exclude(pk=self.pk).delete()

        return super().save(*args, **kwargs)

    def generate_key(self):
        return get_random_string(length=64)

    def is_valid(self):
        return self.is_active and (self.expires is None or self.expires > datetime.now())

    def __str__(self):
        return f"Token para {self.user.username} en {self.app_name}"

class LoginAttempt(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'success', 'Éxito'
        FAILED = 'failed', 'Fallido'

    username = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip_address = models.CharField(max_length=45)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices)

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.username} - {self.status} - {self.timestamp}"

class ModuleCategory(ModelBase):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Module Category'
        verbose_name_plural = 'Module Categories'
        ordering = ['order']
        indexes = [models.Index(fields=['is_active', 'order']),]

    def __str__(self):
        return self.name

class Module(ModelBase):
    category = models.ForeignKey(ModuleCategory, on_delete=models.CASCADE, verbose_name='Category', db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    needs_permission = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['category__order', 'order']


    def __str__(self):
        return self.name

class ModulePermission(ModelBase):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions', db_index=True)
    code_name = models.SlugField(max_length=100, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Module Permission'
        verbose_name_plural = 'Module Permissions'


    def __str__(self):
        return f"{self.module.name} | {self.name}"

    @property
    def full_code_name(self):
        return f"{self.module.code_name}.{self.code_name}" if hasattr(self.module,'code_name') else f"module_{self.module.id}.{self.code_name}"

class AccessGroup(ModelBase):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='access_group', db_index=True)
    description = models.TextField(blank=True, null=True)
    is_super_admin = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = 'Access Group'
        verbose_name_plural = 'Access Groups'

    def __str__(self):
        return f"{self.group.name} - {self.description}"

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if self.is_super_admin:
            if creating or AccessGroup.objects.filter(pk=self.pk, is_super_admin=True).exists():
                self.group.permissions.set(Permission.objects.all())

class AccessGroupModule(ModelBase):
    access_group = models.ForeignKey(AccessGroup, on_delete=models.CASCADE, db_index=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, db_index=True)
    permissions = models.ManyToManyField(ModulePermission, blank=True)
    can_view = models.BooleanField(default=True, db_index=True)
    can_edit = models.BooleanField(default=False, db_index=True)
    can_delete = models.BooleanField(default=False, db_index=True)
    can_manage = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = 'Access Group Module'
        verbose_name_plural = 'Access Group Modules'

    def __str__(self):
        return f"{self.access_group} - {self.module}"

class SystemRol(ModelBase):
    name = models.CharField( max_length=150,verbose_name="Name",unique=True,error_messages={'unique': "Role name must be unique"},db_index=True)
    name_key = models.CharField(max_length=50, verbose_name='Key Name',unique=True,error_messages={'unique': "Role key name must be unique"},db_index=True)
    description = models.TextField(verbose_name='Description', null=True,blank=True)
    is_active = models.BooleanField(default=True,verbose_name='Is Active?',db_index=True)

    class Meta:
        verbose_name = 'System Role'
        verbose_name_plural = 'System Roles'


    def __str__(self):
        return self.name

class Person(ModelBase):
    names = models.CharField(default='', max_length=100, verbose_name=u"Names")
    surname1 = models.CharField(default='', max_length=50, verbose_name=u"1er Surname")
    surname2 = models.CharField(default='', max_length=50, verbose_name=u"2do Surname")
    email = models.CharField(default='', max_length=200, verbose_name=u"Persona email")
    mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name="Mobile number")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Phone number")
    user = models.ForeignKey(User, null=False,blank=False, on_delete=models.CASCADE)
    dni = models.CharField(max_length=15,null=False,blank=False, verbose_name=u"Persona Dni")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date of birth")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country of birth")
    photo = models.ImageField(upload_to=person_photo_path,null=True,blank=True,verbose_name="Profile photo",storage=FileSystemStorage(),help_text="Format: JPG, PNG,")

    class Meta:
        verbose_name = 'Person'

    @property
    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return '/static/images/users/user.png'

    def get_user_permissions(self):
        if not self.user:
            return set()
        permissions = set()
        permissions.update(self.user.user_permissions.all())
        for group in self.access_groups.all():
            permissions.update(group.group.permissions.all())
            for agm in group.accessgroupmodule_set.all():
                permissions.update(agm.permissions.all())

        return {f"{perm.content_type.app_label}.{perm.codename}" for perm in permissions}

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

    def my_profiles(self):
        return ProfileSystemRol.objects.filter(pk__in=self.profileuser_set.values_list('profilesystemrol__id', flat=True).filter(status=True,is_active=True,profilesystemrol__is_active=True))

    def main_profile(self):
        filters = {'status': True,'is_active': True,'profilesystemrol__is_active': True}
        queryset = self.profileuser_set.filter(**filters)
        profile_id = queryset.filter(profilesystemrol__is_main=True).order_by('-id').values_list('profilesystemrol__id',flat=True).first() or queryset.order_by('-id').values_list('profilesystemrol__id', flat=True).first()
        return ProfileSystemRol.objects.get(pk=profile_id) if profile_id else None

class ProfileUser(ModelBase):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=u"Person")
    is_active = models.BooleanField(default=True, verbose_name=u'¿Is Active?')
    access_groups = models.ManyToManyField(AccessGroup, blank=True, related_name='profiles')

    def grupos(self):
        from django.contrib.auth.models import Group
        return Group.objects.filter(access_group__in=self.access_groups.all()).values_list('id', flat=True)

    def __str__(self):
        return u'%s' % self.person

    class Meta:
        verbose_name = u"Perfil de Usuario"
        verbose_name_plural = u"Perfiles de Usuarios"

    def groups(self):
        return self.access_groups.values_list('group_id', flat=True)

class ProfileSystemRol(ModelBase):
    profile = models.ForeignKey(ProfileUser, null=True, on_delete=models.CASCADE, verbose_name=u"User Profile")
    system_rol = models.ForeignKey(SystemRol, null=True, on_delete=models.CASCADE, verbose_name=u"Sistem Rol")
    is_active = models.BooleanField(default=True, verbose_name=u'¿Is Active?')
    is_main = models.BooleanField(default=False, verbose_name=u'¿Is Main?')

    def __str__(self):
        return u'%s (Active: [%s] - Main:[%s)' % (self.system_rol.name_key, 'Yes' if self.is_active else 'NO', 'Yes' if self.is_main else 'NO')

    class Meta:
        verbose_name = u"Perfil de Usuario - Rol"
        verbose_name_plural = u"Perfiles de Usuarios - Roles"

    def my_modules(self):

        if self.profile.person.user.is_superuser:
            return Module.objects.filter(is_active=True,status=True).distinct()
        access_group_modules = AccessGroupModule.objects.filter(access_group__in=self.profile.access_groups.all(),module__is_active=True,can_view=True,status=True).select_related('module')
        module_ids = access_group_modules.values_list('module_id', flat=True).distinct()
        modules = Module.objects.filter(id__in=module_ids,is_active=True,status=True).order_by('category__order', 'order')
        return modules

    def my_notifications(self):
        return Notification.objects.filter(status=True, receiver=self.profile.person, profile=self,is_read=False, is_active=True,datetime_visible__gte=datetime.now())

class Notification(ModelBase):
    title = models.CharField(verbose_name=u'Tittle', max_length=300)
    body = models.TextField(verbose_name=u'Body')
    receiver = models.ForeignKey(Person, related_name='+', verbose_name=u'Recipient', on_delete=models.CASCADE, db_index=True)
    url = models.CharField(verbose_name=u'URL', max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name=u'¿Is Read?')
    datetime_read = models.DateTimeField(blank=True, null=True, verbose_name=u'Date and time read')
    is_active = models.BooleanField(default=True, verbose_name=u'¿Is Active?')
    datetime_visible = models.DateTimeField(blank=True, null=True, verbose_name=u'Visible date and time')
    priority = models.IntegerField(choices=Priorities.CHOICES, default=Priorities.BAJA, verbose_name=u'Priority')
    profile = models.ForeignKey(ProfileSystemRol, related_name='+', null=True, blank=True, db_index=True, verbose_name=u'Perfil', on_delete=models.CASCADE)
    type = models.IntegerField(choices=Types.CHOICES, default=Types.MESSAGE, verbose_name=u'Notification Type')

    def __str__(self):
        return u'Notificación: %s - Para: %s' % (self.title, self.receiver)

    class Meta:
        verbose_name = u"Notificación"
        verbose_name_plural = u"Notificaciones"
        ordering = ['receiver']

class Language(ModelBase):
    code = models.CharField(max_length=10,unique=True,db_index=True)
    name = models.CharField(max_length=100,db_index=True)
    icon = models.CharField(max_length=100,db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = u"Lenguage"
        verbose_name_plural = 'Languages'
        ordering = ['order']

    def __str__(self):
        return self.name

class Level(ModelBase):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='levels', db_index=True)
    name = models.CharField(max_length=50, db_index=True)
    short_name = models.CharField(max_length=10, db_index=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    thumbnail = models.ImageField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())

    class Meta:
        verbose_name = 'Language Level'
        verbose_name_plural = 'Language Levels'
        ordering = ['order']
        unique_together = ('language', 'short_name')

    def __str__(self):
        return f"{self.language.code} - {self.name}"


# class TopicCategory(ModelBase):
#     language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='topic_categories', db_index=True)
#     name = models.CharField(max_length=100, db_index=True)
#     description = models.TextField(blank=True)
#     icon = models.CharField(max_length=50, blank=True, null=True)
#     order = models.PositiveIntegerField(default=0, db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#
#     class Meta:
#         verbose_name = 'Topic Category'
#         verbose_name_plural = 'Topic Categories'
#         ordering = ['order']
#
#     def __str__(self):
#         return f"{self.language.code} - {self.name}"
#
#
# class LearningModule(ModelBase):
#     level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='learning_modules', null=True, blank=True,db_index=True)
#     topic_category = models.ForeignKey(TopicCategory, on_delete=models.CASCADE,related_name='learning_modules', null=True, blank=True, db_index=True)
#     title = models.CharField(max_length=255, db_index=True)
#     description = models.TextField(blank=True)
#     thumbnail = models.ImageField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#     order = models.PositiveIntegerField(default=0, db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#     estimated_duration = models.PositiveIntegerField(default=30, help_text="Duración estimada en minutos")
#     is_premium = models.BooleanField(default=False, db_index=True)
#
#     class Meta:
#         verbose_name = 'Learning Module'
#         verbose_name_plural = 'Learning Modules'
#         ordering = ['order']
#         constraints = [models.CheckConstraint(check=models.Q(level__isnull=False) | models.Q(topic_category__isnull=False),name='learning_module_has_level_or_topic')]
#
#     def __str__(self):
#         prefix = self.level.name if self.level else self.topic_category.name
#         return f"{prefix} - {self.title}"
#
#
# class LearningContent(ModelBase):
#     CONTENT_TYPES = [
#         ('vocabulary', 'Vocabulario'),
#         ('grammar', 'Gramática'),
#         ('pronunciation', 'Pronunciación'),
#         ('culture', 'Cultura'),
#         ('dialogue', 'Diálogo'),
#         ('reading', 'Lectura'),
#         ('listening', 'Escucha'),
#     ]
#
#     module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='contents', db_index=True)
#     title = models.CharField(max_length=255, db_index=True)
#     content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, db_index=True)
#     text_content = models.TextField(blank=True)
#     audio = models.FileField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#     image = models.ImageField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#     video_url = models.URLField(blank=True)
#     order = models.PositiveIntegerField(default=0, db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#     is_free = models.BooleanField(default=False, db_index=True)
#
#     class Meta:
#         verbose_name = 'Learning Content'
#         verbose_name_plural = 'Learning Contents'
#         ordering = ['order']
#
#     def __str__(self):
#         return f"{self.module.title} - {self.title}"
#
#
# class Exercise(ModelBase):
#     TYPE_CHOICES = [
#         ('mcq', 'Opción múltiple'),
#         ('fill_blank', 'Completar espacios'),
#         ('drag_drop', 'Arrastrar y soltar'),
#         ('match', 'Unir pares'),
#         ('order', 'Ordenar secuencia'),
#         ('speaking', 'Práctica de habla'),
#         ('listening', 'Comprensión auditiva'),
#         ('writing', 'Escritura'),
#     ]
#
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Fácil'),
#         ('medium', 'Medio'),
#         ('hard', 'Difícil'),
#     ]
#
#     module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='exercises', db_index=True)
#     content = models.ForeignKey(LearningContent, on_delete=models.SET_NULL,null=True, blank=True, related_name='exercises', db_index=True)
#     title = models.CharField(max_length=255, db_index=True)
#     description = models.TextField(blank=True)
#     max_score = models.PositiveIntegerField(default=100)
#     order = models.PositiveIntegerField(default=0, db_index=True)
#     exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mcq', db_index=True)
#     difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium', db_index=True)
#     is_active = models.BooleanField(default=True, db_index=True)
#     time_limit = models.PositiveIntegerField(null=True, blank=True,help_text="Límite de tiempo en segundos (opcional)")
#     is_premium = models.BooleanField(default=False, db_index=True)
#
#     class Meta:
#         verbose_name = 'Exercise'
#         verbose_name_plural = 'Exercises'
#         ordering = ['order']
#
#     def __str__(self):
#         return f"{self.module.title} - {self.title}"
#
#
# class Question(ModelBase):
#     exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='questions', db_index=True)
#     text = models.TextField(blank=True)  # Pregunta o texto base
#     audio = models.FileField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#     image = models.ImageField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#     explanation = models.TextField(blank=True)
#     order = models.PositiveIntegerField(default=0, db_index=True)
#     points = models.PositiveIntegerField(default=10)
#
#     class Meta:
#         verbose_name = 'Question'
#         verbose_name_plural = 'Questions'
#         ordering = ['order']
#
#     def __str__(self):
#         return f"Q{self.order} - {self.exercise.title}"
#
#
# class Choice(ModelBase):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', db_index=True)
#     text = models.CharField(max_length=255)
#     is_correct = models.BooleanField(default=False, db_index=True)
#     feedback = models.CharField(max_length=255, blank=True)
#
#     class Meta:
#         verbose_name = 'Choice'
#         verbose_name_plural = 'Choices'
#
#     def __str__(self):
#         return f"Choice for Q{self.question.id}: {self.text}"
#
#
# class ExamSimulator(ModelBase):
#     name = models.CharField(max_length=255, db_index=True)
#     language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='exam_simulators', db_index=True)
#     level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='exam_simulators', db_index=True)
#     description = models.TextField(blank=True)
#     duration = models.PositiveIntegerField(help_text="Duración en minutos")
#     passing_score = models.PositiveIntegerField(default=70)
#     attempts_allowed = models.PositiveIntegerField(default=3)
#     is_active = models.BooleanField(default=True, db_index=True)
#     is_premium = models.BooleanField(default=False, db_index=True)
#     thumbnail = models.ImageField(upload_to=learning_content_path, null=True, blank=True,storage=FileSystemStorage())
#
#     class Meta:
#         verbose_name = 'Exam Simulator'
#         verbose_name_plural = 'Exam Simulators'
#
#     def __str__(self):
#         return f"{self.name} ({self.level.short_name})"
#
#
# class UserLanguageProgress(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_progress', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='language_progress', db_index=True)
#     language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='user_progress', db_index=True)
#     current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
#     daily_goal = models.PositiveIntegerField(default=20, help_text="Minutos diarios objetivo")
#     streak = models.PositiveIntegerField(default=0, help_text="Días consecutivos aprendiendo")
#     last_active = models.DateField(null=True, blank=True, db_index=True)
#     total_xp = models.PositiveIntegerField(default=0, help_text="Experiencia total acumulada")
#     total_time_spent = models.PositiveIntegerField(default=0, help_text="Tiempo total en minutos")
#
#     class Meta:
#         verbose_name = 'User Language Progress'
#         verbose_name_plural = 'User Language Progresses'
#         unique_together = ('user', 'language')
#
#     def __str__(self):
#         return f"{self.user.username} - {self.language.name} progress"
#
#
# class UserModuleProgress(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='module_progress', db_index=True)
#     module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='user_progress', db_index=True)
#     completed = models.BooleanField(default=False, db_index=True)
#     completion_date = models.DateTimeField(null=True, blank=True, db_index=True)
#     score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
#     attempts = models.PositiveIntegerField(default=0)
#     time_spent = models.PositiveIntegerField(default=0, help_text="Tiempo en minutos")
#
#     class Meta:
#         verbose_name = 'User Module Progress'
#         verbose_name_plural = 'User Module Progresses'
#         unique_together = ('user', 'module')
#
#     def __str__(self):
#         return f"{self.user.username} - {self.module.title} progress"
#
#
# class UserExerciseAttempt(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_attempts', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='exercise_attempts', db_index=True)
#     exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='attempts', db_index=True)
#     start_time = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(null=True, blank=True, db_index=True)
#     score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
#     completed = models.BooleanField(default=False, db_index=True)
#     time_spent = models.PositiveIntegerField(default=0, help_text="Tiempo en segundos")
#
#     class Meta:
#         verbose_name = 'User Exercise Attempt'
#         verbose_name_plural = 'User Exercise Attempts'
#
#     def __str__(self):
#         return f"{self.user.username} - {self.exercise.title} attempt"
#
#
# class UserExamAttempt(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='exam_attempts', db_index=True)
#     exam = models.ForeignKey(ExamSimulator, on_delete=models.CASCADE, related_name='attempts', db_index=True)
#     start_time = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(null=True, blank=True, db_index=True)
#     score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
#     passed = models.BooleanField(default=False, db_index=True)
#     completed = models.BooleanField(default=False, db_index=True)
#     time_spent = models.PositiveIntegerField(default=0, help_text="Tiempo en minutos")
#
#     class Meta:
#         verbose_name = 'User Exam Attempt'
#         verbose_name_plural = 'User Exam Attempts'
#
#     def __str__(self):
#         return f"{self.user.username} - {self.exam.name} attempt"
#
#
# class UserDailyGoal(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='daily_goals', db_index=True)
#     date = models.DateField(db_index=True)
#     minutes_completed = models.PositiveIntegerField(default=0)
#     goal_achieved = models.BooleanField(default=False, db_index=True)
#     xp_earned = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         verbose_name = 'User Daily Goal'
#         verbose_name_plural = 'User Daily Goals'
#         unique_together = ('user', 'date')
#
#     def __str__(self):
#         return f"{self.user.username} - {self.date} goal"
#
#
# class Achievement(ModelBase):
#     name = models.CharField(max_length=100, db_index=True)
#     description = models.TextField()
#     icon = models.CharField(max_length=50)
#     xp_reward = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True, db_index=True)
#
#     class Meta:
#         verbose_name = 'Achievement'
#         verbose_name_plural = 'Achievements'
#
#     def __str__(self):
#         return self.name
#
#
# class UserAchievement(ModelBase):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', db_index=True)
#     person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='achievements', db_index=True)
#     achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_achievements',db_index=True)
#     date_unlocked = models.DateTimeField(auto_now_add=True)
#     notified = models.BooleanField(default=False, db_index=True)
#
#     class Meta:
#         verbose_name = 'User Achievement'
#         verbose_name_plural = 'User Achievements'
#         unique_together = ('user', 'achievement')
#
#     def __str__(self):
#         return f"{self.user.username} - {self.achievement.name}"