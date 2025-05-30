from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Campos adicionales (opcional)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'auth_user'