from django import forms

class BusquedaForm(forms.Form):
    palabra_clave = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Inteligencia artificial, Albert Einstein, Machine Learning...'
        }),
        label='🔍 Tema a buscar en Wikipedia',
        help_text='Ingresa cualquier tema educativo, científico o histórico'
    )
    
    email_destino = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@gmail.com (opcional)'
        }),
        label='📧 Enviar resultados a (Gmail)',
        help_text='Opcional: Recibe los resultados en tu correo electrónico'
    )