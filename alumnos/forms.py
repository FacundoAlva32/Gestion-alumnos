from django import forms
from .models import Alumno

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'email', 'edad', 'carrera', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Carrera'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        
class EnvioEmailForm(forms.Form):
    email_destino = forms.EmailField(
        label='Email destino',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@gmail.com',
            'required': 'true'
        }),
        help_text='Ingresa el email donde quieres enviar el PDF'
    )