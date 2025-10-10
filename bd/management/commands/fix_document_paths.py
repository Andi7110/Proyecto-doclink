from django.core.management.base import BaseCommand
from bd.models import ConsultaMedica

class Command(BaseCommand):
    help = 'Limpia rutas antiguas de documentos_adjuntos'

    def handle(self, *args, **options):
        updated_count = 0
        for consulta in ConsultaMedica.objects.filter(documentos_adjuntos__startswith='consultas/'):
            consulta.documentos_adjuntos = None
            consulta.save()
            self.stdout.write(f"Limpiado documentos_adjuntos para consulta {consulta.id_consulta_medica}")
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Se limpiaron {updated_count} rutas antiguas.'))