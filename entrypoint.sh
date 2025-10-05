#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

echo "=== Iniciando aplicación Django ==="

# Verificar variables de entorno críticas
echo "Verificando variables de entorno..."
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY no está definida"
    exit 1
fi
if [ -z "$DATABASE_URL" ]; then
    echo "ADVERTENCIA: DATABASE_URL no está definida, usando SQLite por defecto"
fi
echo "Variables de entorno verificadas"

# 1. Recopilar todos los archivos estáticos en el directorio STATIC_ROOT
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# 2. Aplicar las migraciones de la base de datos
echo "Aplicando migraciones de la base de datos..."
python manage.py migrate

# 3. Cargar datos iniciales desde fixtures
echo "Cargando datos iniciales..."
python manage.py loaddata bd/fixtures/initial_data.json

# 4. Crear roles iniciales si no existen
echo "Creando roles iniciales..."
python manage.py shell -c "
from bd.models import Rol
roles = [
    ('medico', 'Rol para médicos del sistema'),
    ('paciente', 'Rol para pacientes del sistema'),
    ('admin', 'Rol para administradores del sistema')
]
for nombre, desc in roles:
    rol, created = Rol.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': desc}
    )
    if created:
        print(f'Rol {nombre} creado')
    else:
        print(f'Rol {nombre} ya existe')
print('Roles verificados')
" 2>/dev/null || echo "Advertencia: No se pudieron crear roles automáticamente"

# 4. Iniciar el servidor de Gunicorn
# Dokploy (y la mayoría de plataformas) proveen una variable de entorno $PORT
# Si no está definida, usar puerto 8000 por defecto
PORT=${PORT:-8000}
echo "Iniciando servidor Gunicorn en puerto $PORT..."
exec gunicorn Donlink.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120