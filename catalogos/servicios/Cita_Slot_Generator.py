from datetime import datetime, timedelta, time
from django.utils import timezone
from catalogos.models import *
from modulos.models import Cita
from django.utils import timezone
from django.db.models import Q

def generar_slots_disponibles(fecha_inicio, fecha_fin):
    SlotDisponible.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
        disponible=True
    ).delete()
    
    fecha_actual = fecha_inicio
    slots_creados = 0
    
    while fecha_actual <= fecha_fin:
        dia_semana = fecha_actual.isoweekday()
        
        # 1. Buscar disponibilidades temporales primero
        disp_temporales = DisponibilidadTemporal.objects.filter(
            fecha_inicio__lte=fecha_actual,
            fecha_fin__gte=fecha_actual,
            activo=True,
            dias_semana__contains=dia_semana
        )
        
        if disp_temporales.exists():
            # Usar las disponibilidades temporales
            for disp in disp_temporales:
                slots_creados += _generar_slots_para_horario(
                    disp.profesional_salud,
                    disp.consultorio,
                    fecha_actual,
                    disp.hora_inicio,
                    disp.hora_fin,
                    dia_semana
                )
        else:
            # Usar horarios regulares
            horarios = Horario.objects.filter(dia=dia_semana)
            for horario in horarios:
                slots_creados += _generar_slots_para_horario(
                    horario.profesional_salud,
                    horario.consultorio,
                    fecha_actual,
                    horario.hora_inicio,
                    horario.hora_fin,
                    dia_semana,
                    horario.duracion_cita
                )
        
        fecha_actual += timedelta(days=1)
    
    return slots_creados

def _generar_slots_para_horario(profesional_salud, consultorio, fecha, hora_inicio, hora_fin, dia_semana, duracion=30):
    """Función auxiliar para generar slots individuales"""
    hora_actual = hora_inicio
    duracion_td = timedelta(minutes=duracion)
    slots_creados = 0
    
    while True:
        hora_fin_slot = (datetime.combine(fecha, hora_actual) + duracion_td).time()
        
        if hora_fin_slot > hora_fin:
            break
        
        # Verificar si ya existe cita
        if not Cita.objects.filter(
            slot__fecha=fecha,
            slot__hora_inicio=hora_actual,
            slot__consultorio=consultorio,
            slot__profesional_salud=profesional_salud  # Cambiado para usar profesional_salud directamente
        ).exists():
            SlotDisponible.objects.create(
                profesional_salud=profesional_salud,  # Campo principal
                consultorio=consultorio,
                fecha=fecha,
                hora_inicio=hora_actual,
                hora_fin=hora_fin_slot,
                disponible=True,
                area=profesional_salud.idArea  # Usando idArea del profesional
            )
            slots_creados += 1
        
        hora_actual = hora_fin_slot
    
    return slots_creados


#eliminar_slots_disponibles si la fecha ya paso a la fecha actual
def eliminar_slots_disponibles():
    ahora = timezone.now()
    slots_eliminados, _ = SlotDisponible.objects.filter(
        Q(fecha__lt=ahora.date()) |
        Q(fecha=ahora.date(), hora_inicio__lt=ahora.time()),  # Cambiado a hora_inicio
        disponible=True
    ).delete()
    return slots_eliminados