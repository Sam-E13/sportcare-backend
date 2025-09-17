# Ejemplo en signals.py
from datetime import date, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from catalogos.models import *
from catalogos.servicios.Cita_Slot_Generator import generar_slots_disponibles, eliminar_slots_disponibles
from modulos.models import *

@receiver(post_save, sender=DisponibilidadTemporal)
@receiver(post_save, sender=Horario)
@receiver(post_delete, sender=Cita)
def actualizar_slots(sender, instance, **kwargs):
    hoy = date.today()
    fin = hoy + timedelta(days=14) # Cambia el rango según sea necesario
    generar_slots_disponibles(hoy, fin)
    eliminar_slots_disponibles()