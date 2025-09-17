# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from modulos.models import *
from catalogos.models import *
from .models import *

# Signal para crear notificaciones al aceptar o cancelar una cita
@receiver(post_save, sender=Cita)
def crear_notificacion_cita(sender, instance, created, **kwargs):
    if not created:  # Solo cuando se actualiza
        if instance.estado == 'Confirmada':
            Notificacion.objects.create(
                user=instance.atleta.user,  
                titulo="Cita Confirmada",
                mensaje=f"Tu cita para {instance.area.nombre} ha sido confirmada.",
                tipo="cita_confirmada",
                leida=False,
                creada_el = instance.actualizado_el,
            )
        elif instance.estado == 'Cancelada':
            Notificacion.objects.create(
                user=instance.atleta.user,
                titulo="Cita Cancelada",
                mensaje=f"Tu cita para {instance.area.nombre} ha sido cancelada.",
                tipo="cita_cancelada",
                leida=False,
                creada_el = instance.actualizado_el,

            )

# Signal para crear notificaciones al profesional al crear una nueva cita
@receiver(post_save, sender=Cita)
def crear_notificacion_profesional(sender, instance, created, **kwargs):
    if created:
          # Creamos la notificación solo si la cita es nueva
        Notificacion.objects.create(
            user=instance.profesional_salud.user,  # Suponiendo que ProfesionalSalud tiene FK a User
            titulo="Nueva cita programada",
            mensaje=f"Se ha programado una nueva cita el dia {instance.slot.fecha}  a las {instance.slot.hora_inicio} con {instance.atleta.nombre} en el Área: {instance.area.nombre} en el Consultorio: {instance.consultorio.nombre}.",
            tipo="mensaje",
            leida=False,
            creada_el = instance.creado_el,
        )

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from modulos.models import Cita
from .models import Notificacion

# Detectar reagendamiento (cambio de slot)
@receiver(pre_save, sender=Cita)
def detectar_reagendamiento(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = Cita.objects.get(pk=instance.pk)
            if anterior.slot_id != instance.slot_id:
                instance._reagendado = True
                instance._slot_anterior = anterior.slot
        except Cita.DoesNotExist:
            pass

# Crear notificaciones al reagendar
@receiver(post_save, sender=Cita)
def notificar_reagendamiento(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_reagendado') and instance._reagendado:
        slot_anterior = getattr(instance, '_slot_anterior', None)
        # Notificación para el atleta
        Notificacion.objects.create(
            user=instance.atleta.user,
            titulo="Cita Reagendada",
            mensaje=f"Tu cita de {instance.area.nombre} fue reagendada a {instance.slot.fecha} {instance.slot.hora_inicio}. "
                    f"Anterior: {slot_anterior.fecha} {slot_anterior.hora_inicio}" if slot_anterior else
                    f"Tu cita de {instance.area.nombre} fue reagendada a {instance.slot.fecha} {instance.slot.hora_inicio}.",
            tipo="cita_reagendada",
        )
        # Notificación para el profesional
        Notificacion.objects.create(
            user=instance.profesional_salud.user,
            titulo="Cita Reagendada",
            mensaje=f"La cita con {instance.atleta.nombre} fue reagendada a {instance.slot.fecha} {instance.slot.hora_inicio}.",
            tipo="cita_reagendada",
        )
