from django.db import models

# Create your models here.

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('encargado', 'Encargado'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.rol})"