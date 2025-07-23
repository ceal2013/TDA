from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

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
    

class Habitacion(models.Model):
    numero_habitacion = models.CharField(max_length=10, unique=True)
    capacidad = models.PositiveIntegerField()
    orientacion = models.CharField(max_length=50, blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Habitación {self.numero_habitacion}"

    def tiene_pasajeros_activos(self):
        return self.reservas_habitacion.filter(
            reserva__estado='activa'
        ).exists()

class Pasajero(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Reserva(models.Model):
    ESTADOS = (
        ('activa', 'Activa'),
        ('anulada', 'Anulada'),
    )
    encargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    pasajero_responsable = models.ForeignKey(Pasajero, on_delete=models.PROTECT)
    fecha_reserva = models.DateField(default=timezone.now)
    hora_reserva = models.TimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')

    def __str__(self):
        return f"Reserva #{self.id} - Responsable: {self.pasajero_responsable.nombre}"

    def calcular_total(self):
        total = 0
        for rh in self.reservas_habitacion.all():
            noches = (rh.fecha_checkout - rh.fecha_checkin).days
            total += rh.cantidad_pasajeros * noches * 20000
        self.total = total
        self.save()
        return total

class ReservaHabitacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='reservas_habitacion')
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='reservas_habitacion')
    fecha_checkin = models.DateField()
    fecha_checkout = models.DateField()
    cantidad_pasajeros = models.PositiveIntegerField()

    def clean(self):
        if self.cantidad_pasajeros != self.habitacion.capacidad:
            raise ValidationError("La cantidad de pasajeros debe coincidir con la capacidad de la habitación.")

    def __str__(self):
        return f"{self.habitacion} ({self.fecha_checkin} a {self.fecha_checkout})"

class PasajeroHabitacion(models.Model):
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    reserva_habitacion = models.ForeignKey(ReservaHabitacion, on_delete=models.CASCADE)
    es_responsable = models.BooleanField(default=False)
    esta_alojado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pasajero.nombre} en {self.reserva_habitacion}"