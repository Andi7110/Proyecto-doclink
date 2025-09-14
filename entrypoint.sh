#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

echo "=== Iniciando aplicación Django ==="

# 1. Recopilar todos los archivos estáticos en el directorio STATIC_ROOT
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# 2. Aplicar las migraciones de la base de datos
echo "Aplicando migraciones de la base de datos..."
python manage.py migrate

# 3. Iniciar el servidor de Gunicorn
# Dokploy (y la mayoría de plataformas) proveen una variable de entorno $PORT
# Si no está definida, usar puerto 8000 por defecto
PORT=${PORT:-8000}
echo "Iniciando servidor Gunicorn en puerto $PORT..."
exec gunicorn Donlink.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120