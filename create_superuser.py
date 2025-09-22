#!/usr/bin/env python
import os
import django
import sys

# Agregar el directorio base al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SportCareIdet.settings_production')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    
    # Datos del superusuario (puedes personalizar estos valores)
    username = 'admin'
    email = 'admin@sportcare.com'
    password = 'Admin123!'  # Cambia este password por uno seguro
    
    # Verificar si ya existe un superusuario
    if not User.objects.filter(is_superuser=True).exists():
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print('✅ Superusuario creado exitosamente!')
            print(f'👤 Usuario: {username}')
            print(f'📧 Email: {email}')
            print(f'🔑 Password: {password}')
            print('⚠️  IMPORTANTE: Cambia el password después de iniciar sesión!')
        except Exception as e:
            print(f'❌ Error al crear superusuario: {e}')
    else:
        print('ℹ️  Ya existe un superusuario en la base de datos')

if __name__ == '__main__':
    create_superuser()