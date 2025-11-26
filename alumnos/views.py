from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone  # ¡AGREGA ESTA LÍNEA!
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from .models import Alumno
from .forms import AlumnoForm

@login_required
def lista_alumnos(request):
    alumnos = Alumno.objects.filter(usuario=request.user)
    return render(request, 'alumnos/lista_alumnos.html', {'alumnos': alumnos})

@login_required
def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            alumno.usuario = request.user
            alumno.save()
            messages.success(request, '✅ Alumno agregado correctamente.')
            return redirect('lista_alumnos')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/agregar_alumno.html', {'form': form})

@login_required
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Alumno actualizado correctamente.')
            return redirect('lista_alumnos')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/editar_alumno.html', {'form': form, 'alumno': alumno})

@login_required
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    if request.method == 'POST':
        alumno.delete()
        messages.success(request, '✅ Alumno eliminado correctamente.')
    return redirect('lista_alumnos')

@login_required
def generar_pdf_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    # Crear el PDF con diseño mejorado
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
    
    # Contenido del PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Centrado
        fontName='Helvetica-Bold'
    )
    
    # Título
    title = Paragraph("REPORTE DE ALUMNO", title_style)
    elements.append(title)
    
    # Línea separadora
    elements.append(Spacer(1, 20))
    
    # Información del alumno - SIN etiquetas HTML
    datos_alumno = [
        ['Nombre:', alumno.nombre],
        ['Email:', alumno.email],
        ['Edad:', f'{alumno.edad} años'],
        ['Carrera:', alumno.carrera],
        ['Estado:', alumno.get_estado_display()],
        ['Fecha de Registro:', alumno.fecha_creacion.strftime("%d/%m/%Y %H:%M")],
    ]
    
    # Crear tabla con estilos directos
    tabla = Table(datos_alumno, colWidths=[200, 250])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(tabla)
    elements.append(Spacer(1, 30))
    
    # Pie de página
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1
    )
    
    footer = Paragraph(
        f"Reporte generado el {alumno.fecha_creacion.strftime('%d/%m/%Y %H:%M')} - Sistema de Gestión de Alumnos",
        footer_style
    )
    elements.append(footer)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Crear respuesta
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{alumno.nombre.replace(" ", "_")}.pdf"'
    
    return response

from .forms import EnvioEmailForm  # Agrega esta importación

@login_required
def enviar_pdf_form(request, pk):
    """Vista para que el usuario ingrese el email destino"""
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = EnvioEmailForm(request.POST)
        if form.is_valid():
            email_destino = form.cleaned_data['email_destino']
            return redirect('enviar_pdf_confirmado', pk=pk, email_destino=email_destino)
    else:
        # AUTOCAMBIO: Pre-llenar con el email del ALUMNO, no del usuario
        form = EnvioEmailForm(initial={'email_destino': alumno.email})
    
    return render(request, 'alumnos/enviar_pdf_form.html', {
        'form': form,
        'alumno': alumno
    })

@login_required
def enviar_pdf_confirmado(request, pk, email_destino):
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    try:
        # Generar PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
        elements = []
        styles = getSampleStyleSheet()
        
        # Contenido del PDF (mejorado)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("REPORTE DE ALUMNO", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        datos_alumno = [
            ['Nombre:', alumno.nombre],
            ['Email:', alumno.email],
            ['Edad:', f'{alumno.edad} años'],
            ['Carrera:', alumno.carrera],
            ['Estado:', alumno.get_estado_display()],
            ['Fecha de Registro:', alumno.fecha_creacion.strftime("%d/%m/%Y %H:%M")],
        ]
        
        tabla = Table(datos_alumno, colWidths=[200, 250])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(tabla)
        elements.append(Spacer(1, 30))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )
        
        footer = Paragraph(
            f"Reporte generado el {alumno.fecha_creacion.strftime('%d/%m/%Y %H:%M')} - Sistema de Gestión de Alumnos",
            footer_style
        )
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        
        # Crear y enviar email con Brevo

        # Dentro de la función enviar_pdf_confirmado, en la parte del email:
        email = EmailMessage(
            f'Reporte del Alumno: {alumno.nombre}',
            f'''
            Hola,

            Adjunto encontrarás el reporte en PDF del alumno {alumno.nombre}.

            📋 RESUMEN DEL ALUMNO:
            • Nombre: {alumno.nombre}
            • Email: {alumno.email}
            • Edad: {alumno.edad} años
            • Carrera: {alumno.carrera}
            • Estado: {alumno.get_estado_display()}
            • Fecha de Registro: {alumno.fecha_creacion.strftime("%d/%m/%Y")}

            📧 Información del envío:
            • Reporte enviado por: {request.user.username} ({request.user.email})
            • Email del alumno: {alumno.email}
            • Fecha de envío: {alumno.fecha_creacion.strftime("%d/%m/%Y %H:%M")}

            Saludos cordiales,
            Sistema de Gestión de Alumnos
            ''',
            settings.DEFAULT_FROM_EMAIL,
            [email_destino],
        )
        
        email.attach(
            f'reporte_{alumno.nombre.replace(" ", "_")}.pdf', 
            buffer.getvalue(), 
            'application/pdf'
        )
        email.send()
        
        messages.success(request, f'✅ PDF enviado correctamente a: {email_destino}')
        
    except Exception as e:
        error_msg = f'❌ Error al enviar el PDF: {str(e)}'
        # Log del error para debugging
        print(f"Error enviando PDF: {e}")
        messages.error(request, error_msg)
    
    return redirect('lista_alumnos')