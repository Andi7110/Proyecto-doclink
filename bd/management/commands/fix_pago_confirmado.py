from django.core.management.base import BaseCommand
from bd.models import CitasMedicas
from django.db.models import Q

class Command(BaseCommand):
    help = 'Corrige el campo pago_confirmado para citas con método de pago efectivo'

    def handle(self, *args, **options):
        # Actualizar todas las citas con cualquier variación de efectivo que no estén confirmadas
        citas_actualizadas = CitasMedicas.objects.filter(
            Q(metodo_pago__iexact='efectivo') | Q(metodo_pago__iexact='Efectivo'),
            pago_confirmado=False
        ).update(pago_confirmado=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'Se actualizaron {citas_actualizadas} citas con método de pago efectivo.'
            )
        )