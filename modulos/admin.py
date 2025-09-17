from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import *
# Register your models here.

# Registra el modelo Sport en el panel de administración


def get_all_fields(model):
    return [field.name for field in model._meta.fields]

@admin.register(Cita)
class CitaAdmin(ModelAdmin):
    list_display = get_all_fields(Cita)

@admin.register(Consulta)
class ConsultaAdmin(ModelAdmin):
    list_display = get_all_fields(Consulta)

@admin.register(Estudio)
class EstudioAdmin(ModelAdmin):
    list_display = get_all_fields(Estudio)

@admin.register(ProgramaAsignado)
class ProgramaAsignadoAdmin(ModelAdmin):
    list_display = get_all_fields(ProgramaAsignado)