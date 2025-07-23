from django.shortcuts import render,redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .forms import LoginForm, UsuarioForm, HabitacionForm, PasajeroForm, ReservaForm, ReservaHabitacionFormSet, PasajeroHabitacionForm, PasajeroHabitacionFormSet
from .models import Usuario, Habitacion, Pasajero, Reserva, ReservaHabitacion, PasajeroHabitacion
from .decorators import custom_login_required, role_required
from django.forms import modelformset_factory

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
            messages.success(request, "Reserva creada exitosamente. Ahora asigne los pasajeros.")
            return redirect('asignar_pasajeros', id_reserva=reserva.id_reserva)
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

@custom_login_required
def asignar_pasajeros(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    habitaciones_reservadas = ReservaHabitacion.objects.filter(id_reserva=reserva)

    PasajeroHabitacionFormSet = modelformset_factory(
        PasajeroHabitacion,
        form=PasajeroHabitacionForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        formset = PasajeroHabitacionFormSet(request.POST)
        if formset.is_valid():
            responsable_count = 0
            total_por_habitacion = {}

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    rh = form.cleaned_data['reserva_habitacion']
                    if rh.id_reserva != reserva:
                        messages.error(request, "Asignación no válida: habitación no pertenece a la reserva.")
                        return redirect('listar_reservas')

                    total_por_habitacion.setdefault(rh.id, 0)
                    if form.cleaned_data['esta_alojado']:
                        total_por_habitacion[rh.id] += 1

                    if form.cleaned_data['es_responsable']:
                        responsable_count += 1

            for rh in habitaciones_reservadas:
                if total_por_habitacion.get(rh.id, 0) != rh.cantidad_pasajeros:
                    messages.error(request, f"La habitación {rh.id_habitacion.numero_habitacion} debe tener exactamente {rh.cantidad_pasajeros} pasajeros alojados.")
                    return redirect('asignar_pasajeros', id_reserva=id_reserva)

            if responsable_count != 1:
                messages.error(request, "Debe haber exactamente un pasajero responsable.")
                return redirect('asignar_pasajeros', id_reserva=id_reserva)

            # Guardar datos
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                instance.save()

            messages.success(request, "Pasajeros asignados correctamente.")
            return redirect('listar_reservas')
        else:
            messages.error(request, "Formulario inválido.")
    else:
        existentes = PasajeroHabitacion.objects.filter(reserva_habitacion__in=habitaciones_reservadas)
        formset = PasajeroHabitacionFormSet(queryset=existentes)

    return render(request, 'reservas/asignar_pasajeros.html', {
        'formset': formset,
        'reserva': reserva,
        'habitaciones': habitaciones_reservadas,
    })