from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import *
# Register your models here.

# Registra el modelo Sport en el panel de administración


def get_all_fields(model):
    return [field.name for field in model._meta.fields]

@admin.register(Deporte)
class DeporteAdmin(ModelAdmin):
    list_display = get_all_fields(Deporte)

@admin.register(Atleta)
class AtletaAdmin(ModelAdmin):
    list_display = get_all_fields(Atleta)

@admin.register(AtletaContacto)
class AtletaContactoAdmin(ModelAdmin):
    list_display = get_all_fields(AtletaContacto)

@admin.register(ResponsableAtleta)
class ResponsableAtletaAdmin(ModelAdmin):
    list_display = get_all_fields(ResponsableAtleta)

@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = get_all_fields(Categoria)

@admin.register(Consultorio)
class ConsultorioAdmin(ModelAdmin):
    list_display = get_all_fields(Consultorio)

@admin.register(ProfesionalSalud)
class DeporteAdmin(ModelAdmin):
    list_display = get_all_fields(ProfesionalSalud)

@admin.register(Area)
class AreaAdmin(ModelAdmin):
    list_display = get_all_fields(Area)


@admin.register(Horario)
class HorarioAdmin(ModelAdmin):
    list_display = get_all_fields(Horario)

@admin.register(DisponibilidadTemporal)
class DisponibilidadTemporalAdmin(ModelAdmin):
    list_display = get_all_fields(DisponibilidadTemporal)

@admin.register(SlotDisponible)
class SlotDisponibleAdmin(ModelAdmin):
    list_display = get_all_fields(SlotDisponible)

@admin.register(Entrenador)
class EntrenadorAdmin(ModelAdmin):
    list_display = get_all_fields(Entrenador)

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(ModelAdmin):
    list_display = get_all_fields(SesionEntrenamiento)

@admin.register(Ejercicio)
class EjercicioAdmin(ModelAdmin):
    list_display = get_all_fields(Ejercicio)


@admin.register(ProgramaEntrenamiento)
class ProgramaEntrenamientoAdmin(ModelAdmin):
    list_display = get_all_fields(ProgramaEntrenamiento)
    
@admin.register(GrupoDeportivo)
class GrupoDeportivoAdmin(ModelAdmin):
    list_display = get_all_fields(GrupoDeportivo)

@admin.register(Metodologo)
class MetodologoAdmin(ModelAdmin):
    list_display = get_all_fields(Metodologo)


