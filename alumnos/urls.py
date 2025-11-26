from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_alumnos, name='lista_alumnos'),
    path('agregar/', views.agregar_alumno, name='agregar_alumno'),
    path('editar/<int:pk>/', views.editar_alumno, name='editar_alumno'),
    path('eliminar/<int:pk>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('pdf/<int:pk>/', views.generar_pdf_alumno, name='generar_pdf_alumno'),
    
    # Nueva funcionalidad - Envío a email personalizado
    path('enviar-pdf/<int:pk>/', views.enviar_pdf_form, name='enviar_pdf_form'),
    path('enviar-pdf-confirmado/<int:pk>/<str:email_destino>/', views.enviar_pdf_confirmado, name='enviar_pdf_confirmado'),
]