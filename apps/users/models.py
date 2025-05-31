from django.db import models
from apps.core.models.models import  ModelBase
from django.contrib.auth.models import User, Group


class People(ModelBase):
    email = models.CharField(default='', max_length=200, verbose_name=u"Correo electronico personal")
    phone = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'People'