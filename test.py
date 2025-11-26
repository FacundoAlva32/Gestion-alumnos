import os
import django
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumnos_project.settings')
django.setup()

from django.conf import settings

print("🔍 DIAGNÓSTICO BREVO")
print("=" * 50)

# Mostrar configuración actual (sin mostrar password completa)
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

if settings.EMAIL_HOST_PASSWORD:
    password_preview = settings.EMAIL_HOST_PASSWORD[:10] + "..." + settings.EMAIL_HOST_PASSWORD[-10:]
    print(f"EMAIL_HOST_PASSWORD: {password_preview}")
    print(f"Longitud password: {len(settings.EMAIL_HOST_PASSWORD)} caracteres")
else:
    print("EMAIL_HOST_PASSWORD: ❌ NO CONFIGURADO")

print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)

# Verificar formato de password
if settings.EMAIL_HOST_PASSWORD:
    if settings.EMAIL_HOST_PASSWORD.startswith('xsmtpsib-'):
        print("✅ Formato de password CORRECTO (empieza con xsmtpsib-)")
    else:
        print("❌ Formato de password INCORRECTO - Debe empezar con 'xsmtpsib-'")

# Probar conexión
try:
    print("🧪 Probando envío de email...")
    send_mail(
        'Prueba Brevo - Sistema Alumnos',
        'Este es un email de prueba.',
        settings.DEFAULT_FROM_EMAIL,
        ['lomohijo@gmail.com'],  # Envíatelo a ti mismo
        fail_silently=False,
    )
    print("✅ ¡ÉXITO! Email enviado correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Análisis detallado del error
    error_str = str(e)
    if "535" in error_str and "authentication" in error_str.lower():
        print("\n🔎 ANÁLISIS DEL ERROR 535:")
        print("1. ✅ Servidor SMTP responde (smtp-relay.brevo.com)")
        print("2. ❌ Autenticación falló")
        print("\n🎯 CAUSAS POSIBLES:")
        print("• Password SMTP incorrecto")
        print("• Email (USER) no coincide con la cuenta Brevo")
        print("• Credenciales SMTP no generadas en Brevo")
        print("• Espacios en las credenciales")
        
    print(f"\n💡 SOLUCIÓN:")
    print("1. Ve a: https://app.brevo.com/smtp")
    print("2. Genera NUEVAS credenciales SMTP")
    print("3. Copia EXACTAMENTE la password que empieza con 'xsmtpsib-'")
    print("4. Actualiza el archivo .env")
    print("5. Reinicia el servidor Django")