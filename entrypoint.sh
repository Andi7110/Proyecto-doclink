#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# 1. Recopilar todos los archivos estáticos en el directorio STATIC_ROOT
echo "Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# 2. Aplicar las migraciones de la base de datos
echo "Aplicando migraciones de la base de datos..."
python manage.py migrate

# 3. Iniciar el servidor de Gunicorn
# Dokploy (y la mayoría de plataformas) proveen una variable de entorno $PORT
# Gunicorn debe escuchar en todas las IPs (0.0.0.0) en ese puerto.
echo "Iniciando servidor Gunicorn..."
gunicorn Donlink.wsgi:application --bind 0.0.0.0:$PORT