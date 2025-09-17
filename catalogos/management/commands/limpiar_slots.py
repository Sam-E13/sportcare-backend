from django.core.management.base import BaseCommand
from catalogos.servicios.Cita_Slot_Generator import eliminar_slots_disponibles

class Command(BaseCommand):
    help = 'Elimina slots disponibles que ya pasaron su fecha/hora'

    def handle(self, *args, **options):
        slots_eliminados = eliminar_slots_disponibles()
        self.stdout.write(
            self.style.SUCCESS(
                f'Se eliminaron {slots_eliminados} slots vencidos'
            )
        )