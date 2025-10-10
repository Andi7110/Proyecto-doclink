from django.core.management.base import BaseCommand
from bd.models import ConsultaMedica
import os
import base64

class Command(BaseCommand):
    help = 'Convierte rutas antiguas a base64 si el archivo existe'

    def handle(self, *args, **options):
        updated_count = 0
        for consulta in ConsultaMedica.objects.exclude(documentos_adjuntos__isnull=True).exclude(documentos_adjuntos=''):
            if consulta.documentos_adjuntos.startswith('consultas/'):
                # Es una ruta antigua
                file_path = os.path.join('media', consulta.documentos_adjuntos)
                if os.path.exists(file_path):
                    # Convertir a base64
                    with open(file_path, 'rb') as f:
                        base64_data = base64.b64encode(f.read()).decode('utf-8')
                    consulta.documentos_adjuntos = base64_data
                    consulta.save()
                    self.stdout.write(f"Convertido {file_path} a base64")
                    updated_count += 1
                else:
                    # Archivo no existe, limpiar
                    consulta.documentos_adjuntos = None
                    consulta.save()
                    self.stdout.write(f"Archivo no encontrado, limpiado: {file_path}")
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Se procesaron {updated_count} registros.'))