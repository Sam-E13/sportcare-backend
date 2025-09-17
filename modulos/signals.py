# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from modulos.models import *
from catalogos.models import *
from .models import *

# Signal para Cambiar el estado de una cita a "Completada" cuando la consulta asociada se completa
@receiver(post_save, sender=Consulta)
def cita_cambia_estado_completada(sender, instance, created, **kwargs):
    if created and instance.cita:
        instance.cita.estado = 'Completada'
        instance.cita.save()