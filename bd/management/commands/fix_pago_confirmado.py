from django.core.management.base import BaseCommand
from bd.models import CitasMedicas

class Command(BaseCommand):
    help = 'Corrige el campo pago_confirmado para citas con método de pago efectivo'

    def handle(self, *args, **options):
        # Actualizar todas las citas con efectivo para que aparezcan como confirmadas
        citas_actualizadas = CitasMedicas.objects.filter(
            metodo_pago='efectivo',
            pago_confirmado=False
        ).update(pago_confirmado=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'Se actualizaron {citas_actualizadas} citas con método de pago efectivo.'
            )
        )