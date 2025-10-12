#!/usr/bin/env python
"""
Script para actualizar facturas existentes con los nuevos campos de generación automática
"""
import os
import sys
import django
import uuid
import random
import string
from datetime import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Donlink.settings')
django.setup()

from bd.models import Factura

def generar_codigo_generacion():
    return str(uuid.uuid4()).upper()

def generar_sello_recepcion():
    year = 2025  # Usar 2025 como año actual
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=45))
    return f"{year}{random_chars}"

def generar_numero_control():
    random_part1 = ''.join(random.choices(string.ascii_uppercase, k=3))
    random_part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"DTE-01-{random_part1}{random_part2}"

def generar_documento_interno():
    # Obtener el último número usado
    last_factura = Factura.objects.exclude(documento_interno__isnull=True).exclude(documento_interno='').order_by('-documento_interno').first()
    if last_factura and last_factura.documento_interno:
        try:
            last_num = int(last_factura.documento_interno)
            return str(last_num + 1).zfill(5)
        except ValueError:
            pass
    return "00001"

def main():
    print("Actualizando facturas existentes...")

    facturas = Factura.objects.all()
    updated_count = 0

    for factura in facturas:
        updated = False

        if not factura.codigo_generacion:
            factura.codigo_generacion = generar_codigo_generacion()
            updated = True

        if not factura.sello_recepcion:
            factura.sello_recepcion = generar_sello_recepcion()
            updated = True

        if not factura.numero_control:
            factura.numero_control = generar_numero_control()
            updated = True

        if not factura.documento_interno:
            factura.documento_interno = generar_documento_interno()
            updated = True

        if updated:
            # Guardar sin llamar al método save() para evitar regenerar valores
            Factura.objects.filter(id_factura=factura.id_factura).update(
                codigo_generacion=factura.codigo_generacion,
                sello_recepcion=factura.sello_recepcion,
                numero_control=factura.numero_control,
                documento_interno=factura.documento_interno
            )
            updated_count += 1
            print(f"Actualizada factura ID {factura.id_factura}: Documento Interno {factura.documento_interno}")

    print(f"Proceso completado. {updated_count} facturas actualizadas.")

if __name__ == '__main__':
    main()