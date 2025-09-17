from django.db import models
from django.forms import ValidationError
from catalogos.models import *
from django.core.validators import URLValidator
# Create your models here.

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Completada', 'Completada'),
    ]
    
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name='citas_atleta')
    slot = models.OneToOneField(SlotDisponible, on_delete=models.CASCADE, related_name='citas_slot')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='citas_area')
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE, related_name='citas_consultorio')
    profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE, related_name='citas_profesional')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Pendiente')
    observaciones = models.TextField(blank=True, null=True)
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)
    
    def clean(self):
        # Validar que el slot esté disponible
        if not self.slot.disponible and not self.pk:
            from django.core.exceptions import ValidationError
            raise ValidationError({'slot': 'Este horario ya no está disponible'})
    
    def save(self, *args, **kwargs):
        # Detectar si es reagendamiento (cambio de slot)
        slot_cambiado = False
        if self.pk:
            try:
                anterior = Cita.objects.get(pk=self.pk)
                if anterior.slot_id != self.slot_id:
                    slot_cambiado = True
            except Cita.DoesNotExist:
                pass

        self.clean()  # Ejecutar validaciones

        # Al crear la cita, marcamos el slot como no disponible
        if not self.pk:
            self.slot.disponible = False
            self.slot.save()
        # Si se está reagendando (cambiando slot), NO liberar el slot anterior; solo ocupar el nuevo
        elif slot_cambiado:
            self.slot.disponible = False
            self.slot.save()
            # Mantener el estado en Pendiente tras el reagendamiento si deseas forzarlo
            # self.estado = 'Pendiente'

        super().save(*args, **kwargs)
    
    def __str__(self):
         return f"Cita {self.atleta} - {self.area} - {self.profesional_salud.nombre} el dia {self.slot.fecha} a las {self.slot.hora_inicio}"

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"

#consultas
class Consulta(models.Model):
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name="consultas")
    cita = models.OneToOneField(Cita, on_delete=models.SET_NULL, null=True, blank=True)
    profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE)
    fecha = models.DateField()
    motivo = models.TextField()
    antecedentes_familiares = models.TextField(blank=True, null=True)
    antecedentes_no_patologicos = models.TextField(blank=True, null=True)
    presion_arterial = models.CharField(max_length=20, blank=True, null=True)
    frecuencia_cardiaca = models.CharField(max_length=20, blank=True, null=True)
    frecuencia_respiratoria = models.CharField(max_length=20, blank=True, null=True)
    temperatura = models.CharField(max_length=10, blank=True, null=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Consulta {self.fecha} - {self.atleta}"

    class Meta:
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"

class Estudio(models.Model):
    TIPO_ESTUDIO_CHOICES = [
        ('LAB', 'Análisis de Laboratorio'),
        ('IMG', 'Estudio de Imagen'),
        ('CAR', 'Cardiología'),
        ('NEU', 'Neurológico'),
        ('ODO', 'Odontológico'),
        ('OFT', 'Oftalmológico'),
        ('OTR', 'Otros'),
    ]
    
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name="estudios")
    tipo_estudio = models.CharField(max_length=100, choices=TIPO_ESTUDIO_CHOICES)
    nombre = models.CharField(max_length=200, blank=True, null=True)  # Nombre descriptivo del estudio
    resultado = models.TextField()
    fecha_realizacion = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)
    archivo = models.FileField(upload_to='estudios/%Y/%m/%d/', blank=True, null=True)
    enlace = models.URLField(max_length=500, blank=True, null=True, validators=[URLValidator()])
    observaciones = models.TextField(blank=True, null=True)

    def clean(self):
        if not self.archivo and not self.enlace:
            raise ValidationError("Debe proporcionar un archivo o un enlace para el estudio.")
        if self.archivo and self.enlace:
            raise ValidationError("Solo debe proporcionar un archivo o un enlace, no ambos.")

    def __str__(self):
        return f"{self.get_tipo_estudio_display()} - {self.nombre} ({self.fecha_realizacion})"

    class Meta:
        verbose_name = "Estudio Médico"
        verbose_name_plural = "Estudios Médicos"
        ordering = ['-fecha_realizacion']


class ProgramaAsignado(models.Model):
    programa = models.ForeignKey(ProgramaEntrenamiento, on_delete=models.CASCADE, related_name='asignaciones')
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name='programas_asignados')
    fecha_asignacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ], default='activo')
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.atleta} - {self.programa}"

    class Meta:
        verbose_name = "Asignación de programa"
        verbose_name_plural = "Asignación de programas"
        