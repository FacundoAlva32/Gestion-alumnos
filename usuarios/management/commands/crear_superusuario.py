from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Crear superusuario automáticamente si no existe'

    def handle(self, *args, **options):
        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('✅ Superusuario ya existe'))
            return

        # Crear superusuario
        username = 'admin'
        email = 'admin@sistema.com'
        password = 'admin123'
        
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Superusuario creado:'))
        self.stdout.write(self.style.SUCCESS(f'   Usuario: {username}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
        self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))