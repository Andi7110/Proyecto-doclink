#!/usr/bin/env python
"""
Script para crear los roles iniciales en producción
Ejecutar una sola vez después del despliegue
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Donlink.settings')
sys.path.append(os.path.dirname(__file__))
django.setup()

from bd.models import Rol

def create_initial_roles():
    """Crear roles iniciales si no existen"""
    roles_to_create = [
        {'nombre': 'medico', 'descripcion': 'Rol para médicos del sistema'},
        {'nombre': 'paciente', 'descripcion': 'Rol para pacientes del sistema'},
        {'nombre': 'admin', 'descripcion': 'Rol para administradores del sistema'}
    ]

    created_count = 0
    for rol_data in roles_to_create:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        if created:
            print(f"✅ Rol '{rol.nombre}' creado exitosamente")
            created_count += 1
        else:
            print(f"ℹ️  Rol '{rol.nombre}' ya existe")

    if created_count > 0:
        print(f"\n🎉 Se crearon {created_count} roles nuevos")
    else:
        print("\n✅ Todos los roles ya existen")

if __name__ == '__main__':
    print("🔄 Creando roles iniciales...")
    create_initial_roles()
    print("✅ Proceso completado")