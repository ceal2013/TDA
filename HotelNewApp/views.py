from django.shortcuts import render,redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .forms import LoginForm, UsuarioForm, HabitacionForm, PasajeroForm, ReservaForm, ReservaHabitacionFormSet
from .models import Usuario, Habitacion, Pasajero, Reserva, ReservaHabitacion
from .decorators import custom_login_required, role_required

# Create your views here.
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                usuario = Usuario.objects.get(username=username)

                if check_password(password, usuario.password):
                    # Inicia sesión de forma manual con session
                    request.session['usuario_id'] = usuario.id_usuario
                    request.session['username'] = usuario.username
                    request.session['rol'] = usuario.rol

                    return redirect('home')
                else:
                    messages.error(request, "Contraseña incorrecta.")

            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado.")

    return render(request, 'login.html', {'form': form})


# Vista para home, cualquier usuario logueado puede verla
@custom_login_required
def home(request):
    return render(request, 'home.html')

def user_logout(request):
    request.session.flush()  # Borra la sesión manualmente
    return redirect('login')

# Vistas de usuarios solo para admin
@custom_login_required
@role_required(['admin'])
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@custom_login_required
@role_required(['admin'])
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'accion': 'Crear'})

@custom_login_required
@role_required(['admin'])
def editar_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            nueva_pass = form.cleaned_data['password']
            if not usuario.password.startswith('pbkdf2_'):
                usuario.password = make_password(nueva_pass)
            usuario.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'accion': 'Editar'})

@custom_login_required
@role_required(['admin'])
def eliminar_usuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    usuario.delete()
    return redirect('listar_usuarios')

# Habitaciones

@custom_login_required
def listar_habitaciones(request):
    habitaciones = Habitacion.objects.all()
    return render(request, 'habitaciones/listar_habitaciones.html', {'habitaciones': habitaciones})

@custom_login_required
def crear_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Habitación creada correctamente.")
            return redirect('listar_habitaciones')
    else:
        form = HabitacionForm()
    return render(request, 'habitaciones/form_habitacion.html', {'form': form, 'accion': 'Crear'})

@custom_login_required
def eliminar_habitacion(request, id_habitacion):
    habitacion = get_object_or_404(Habitacion, id=id_habitacion)
    if habitacion.tiene_pasajeros_activos():
        messages.error(request, "No puede eliminar una habitación con pasajeros activos.")
    else:
        habitacion.activa = False
        habitacion.save()
        messages.success(request, "Habitación desactivada correctamente.")
    return redirect('listar_habitaciones')

# Pasajeros

@custom_login_required
def listar_pasajeros(request):
    pasajeros = Pasajero.objects.all()
    return render(request, 'pasajeros/listar_pasajeros.html', {'pasajeros': pasajeros})

@custom_login_required
def crear_pasajero(request):
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pasajero creado correctamente.")
            return redirect('listar_pasajeros')
    else:
        form = PasajeroForm()
    return render(request, 'pasajeros/form_pasajero.html', {'form': form, 'accion': 'Crear'})

# Reservas

@custom_login_required
@transaction.atomic
def listar_reservas(request):
    reservas = Reserva.objects.all()
    return render(request, 'reservas/listar_reservas.html', {'reservas': reservas})

@custom_login_required
@transaction.atomic
def crear_reserva(request):
    if request.method == 'POST':
        reserva_form = ReservaForm(request.POST)
        formset = ReservaHabitacionFormSet(request.POST)
        if reserva_form.is_valid() and formset.is_valid():
            reserva = reserva_form.save(commit=False)
            reserva.encargado_id = request.session['usuario_id']
            reserva.total = 0
            reserva.save()
            formset.instance = reserva
            formset.save()
            reserva.calcular_total()
            messages.success(request, "Reserva creada exitosamente.")
            return redirect('listar_reservas')
        else:
            messages.error(request, "Error al crear la reserva. Revise los datos.")
    else:
        reserva_form = ReservaForm()
        formset = ReservaHabitacionFormSet()
    return render(request, 'reservas/form_reserva.html', {
        'reserva_form': reserva_form,
        'formset': formset,
        'accion': 'Crear'
    })

@custom_login_required
def cancelar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id=id_reserva)
    reserva.estado = 'anulada'
    reserva.save()
    messages.success(request, "Reserva anulada correctamente.")
    return redirect('listar_reservas')