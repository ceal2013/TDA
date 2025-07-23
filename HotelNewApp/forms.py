from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from .models import Usuario, Habitacion, Pasajero, Reserva, ReservaHabitacion, PasajeroHabitacion
from django.forms import modelformset_factory

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su nombre de usuario',
        'required': 'required'
    }))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ingrese su contraseña',
        'required': 'required'
    }))

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'rol']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero_habitacion', 'capacidad', 'orientacion']

class PasajeroForm(forms.ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombre', 'rut']

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['pasajero_responsable']

class ReservaHabitacionForm(forms.ModelForm):
    class Meta:
        model = ReservaHabitacion
        fields = ['habitacion', 'fecha_checkin', 'fecha_checkout', 'cantidad_pasajeros']

from django.forms import inlineformset_factory
ReservaHabitacionFormSet = inlineformset_factory(
    Reserva,
    ReservaHabitacion,
    fields=('habitacion', 'fecha_checkin', 'fecha_checkout', 'cantidad_pasajeros'),
    extra=1,
    can_delete=True,
    validate_min=True
)

class PasajeroHabitacionForm(forms.ModelForm):
    class Meta:
        model = PasajeroHabitacion
        fields = ['pasajero', 'es_responsable', 'esta_alojado']
        widgets = {
            'pasajero': forms.Select(attrs={'class': 'form-select'}),
            'es_responsable': forms.CheckboxInput(),
            'esta_alojado': forms.CheckboxInput(),
        }

PasajeroHabitacionFormSet = modelformset_factory(
    PasajeroHabitacion,
    form=PasajeroHabitacionForm,
    extra=0,
    can_delete=True
)