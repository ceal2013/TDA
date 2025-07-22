from django import forms

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