from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from alumnos.models import Alumno
from .forms import RegistroForm

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Enviar correo de bienvenida con Brevo
            try:
                send_mail(
                    '¡Bienvenido al Sistema de Gestión de Alumnos!',
                    f'Hola {user.username},\n\nGracias por registrarte en nuestro sistema. '
                    'Ahora puedes gestionar tus alumnos y generar reportes en PDF.\n\n'
                    'Funcionalidades disponibles:\n'
                    '• Gestión de alumnos\n'
                    '• Generación de reportes PDF\n'
                    '• Envío de PDFs por email\n'
                    '• Búsqueda en Wikipedia\n\n'
                    'Saludos cordiales,\nEquipo del Sistema',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, '¡Registro exitoso! Se ha enviado un correo de bienvenida.')
            except Exception as e:
                print(f"Error enviando email de bienvenida: {e}")
                messages.warning(request, 'Registro exitoso, pero no se pudo enviar el correo de bienvenida.')
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required
def dashboard_view(request):
    # Obtener estadísticas del usuario
    total_alumnos = Alumno.objects.filter(usuario=request.user).count()
    alumnos_activos = Alumno.objects.filter(usuario=request.user, estado='activo').count()
    alumnos_inactivos = Alumno.objects.filter(usuario=request.user, estado='inactivo').count()
    alumnos_egresados = Alumno.objects.filter(usuario=request.user, estado='egresado').count()
    
    # Últimos alumnos agregados
    ultimos_alumnos = Alumno.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
    
    context = {
        'total_alumnos': total_alumnos,
        'alumnos_activos': alumnos_activos,
        'alumnos_inactivos': alumnos_inactivos,
        'alumnos_egresados': alumnos_egresados,
        'ultimos_alumnos': ultimos_alumnos,
    }
    
    return render(request, 'usuarios/dashboard.html', context)