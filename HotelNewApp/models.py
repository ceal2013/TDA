from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, rol='encargado', **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        user = self.model(username=username, rol=rol, **extra_fields)
        user.set_password(password)  # Aquí se encripta
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'admin')
        return self.create_user(username, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    rol = models.CharField(
        max_length=10,
        choices=[
            ('admin', 'Administrador'),
            ('encargado', 'Encargado'),
        ]
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Importante para entrar al admin

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.username} ({self.rol})"