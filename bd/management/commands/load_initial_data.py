from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
import os

# Comando para cargar datos iniciales
class Command(BaseCommand):
    help = 'Load initial data fixtures'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')

        fixture_path = 'bd/fixtures/initial_data.json'
        # Check if the fixture file exists
        if os.path.exists(fixture_path):
            try:
                with transaction.atomic():
                    call_command('loaddata', fixture_path, verbosity=2)
                self.stdout.write(
                    self.style.SUCCESS('Successfully loaded initial data')
                )
                # Realizar cualquier otra acción necesaria después de cargar los datos
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not load initial data: {e}')
                )
                # Realizar cualquier otra acción necesaria en caso de error
        else:
            self.stdout.write(
                self.style.WARNING(f'Fixture file not found: {fixture_path}')
            )