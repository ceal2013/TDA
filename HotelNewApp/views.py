from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .forms import LoginForm, UsuarioForm
from .models import Usuario

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


def home(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    return render(request, 'home.html')

def user_logout(request):
    request.session.flush()  # Borra la sesión manualmente
    return redirect('login')

def listar_usuarios(request):
    if not request.session.get('usuario_id') or request.session.get('rol') != 'admin':
        return redirect('login')
    
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

def crear_usuario(request):
    if not request.session.get('usuario_id') or request.session.get('rol') != 'admin':
        return redirect('login')
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()  # Ya hace el set_password dentro del form
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'accion': 'Crear'})

def editar_usuario(request, id_usuario):
    if not request.session.get('usuario_id') or request.session.get('rol') != 'admin':
        return redirect('login')

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


def eliminar_usuario(request, id_usuario):
    if not request.session.get('usuario_id') or request.session.get('rol') != 'admin':
        return redirect('login')

    usuario = Usuario.objects.get(id_usuario=id_usuario)
    usuario.delete()
    return redirect('listar_usuarios')