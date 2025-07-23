from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='login/')),  # Redirige a la vista de inicio de sesión
    path('login/', views.login_view, name='login'),  # Coincide con LOGIN_URL
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id_usuario>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id_usuario>/', views.eliminar_usuario, name='eliminar_usuario'),
    # Habitaciones
    path('habitaciones/', views.listar_habitaciones, name='listar_habitaciones'),
    path('habitaciones/crear/', views.crear_habitacion, name='crear_habitacion'),
    path('habitaciones/eliminar/<int:id>/', views.eliminar_habitacion, name='eliminar_habitacion'),

    # Pasajeros
    path('pasajeros/', views.listar_pasajeros, name='listar_pasajeros'),
    path('pasajeros/crear/', views.crear_pasajero, name='crear_pasajero'),

    # Reservas
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/crear/', views.crear_reserva, name='crear_reserva'),
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/asignar_pasajeros/<int:id_reserva>/', views.asignar_pasajeros, name='asignar_pasajeros'),
]
