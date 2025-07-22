from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Coincide con LOGIN_URL
    path('home/', views.home, name='home'),
]
