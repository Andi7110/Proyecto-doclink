from django.core.management.base import BaseCommand
from bd.models import ConsultaMedica

class Command(BaseCommand):
    help = 'Corrige las rutas de documentos_adjuntos que empiecen con "consultas/"'

    def handle(self, *args, **options):
        updated_count = 0
        for consulta in ConsultaMedica.objects.exclude(documentos_adjuntos__startswith='consultas/').exclude(documentos_adjuntos__isnull=True).exclude(documentos_adjuntos=''):
            old_path = consulta.documentos_adjuntos.name
            new_path = f"consultas/{old_path}"
            consulta.documentos_adjuntos.name = new_path
            consulta.save()
            self.stdout.write(f"Updated {old_path} to {new_path}")
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Se actualizaron {updated_count} rutas de documentos.'))