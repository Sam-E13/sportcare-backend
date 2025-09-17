# serializers.py
from rest_framework import serializers
from .models import *
from catalogos.models import Atleta, SlotDisponible

class CitaSerializer(serializers.ModelSerializer):

     # Campos para lectura y mostracion de datos
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    profesional_salud_nombre = serializers.CharField(source='profesional_salud.nombre', read_only=True)
    atleta_nombre = serializers.CharField(source='atleta.nombre', read_only=True)
    slot_hora_inicio = serializers.CharField(source='slot.hora_inicio', read_only=True)
    slot_hora_fin = serializers.CharField(source='slot.hora_fin', read_only=True)
    slot_fecha = serializers.CharField(source='slot.fecha', read_only=True)
    
    class Meta:
        model = Cita
        fields = '__all__'
      

class EstudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudio
        fields = "__all__"
        extra_kwargs = {
            'archivo': {'required': False, 'allow_null': True},
            'enlace': {'required': False, 'allow_null': True}
        }

class ConsultaSerializer(serializers.ModelSerializer):
    # Campos para lectura y mostracion de datos
    profesional_salud_nombre = serializers.CharField(source='profesional_salud.nombre', read_only=True)
    atleta_nombre = serializers.CharField(source='atleta.nombre', read_only=True)

    # Este es el nuevo campo para mostrar descripción de la cita
    cita_descripcion = serializers.SerializerMethodField()


    #campos para insersion y actualizacion de datos
    profesional_salud = serializers.PrimaryKeyRelatedField(queryset=ProfesionalSalud.objects.all())
    atleta = serializers.PrimaryKeyRelatedField(queryset=Atleta.objects.all())
    cita = serializers.PrimaryKeyRelatedField(queryset=Cita.objects.all(), required=False, allow_null=True)

    
    # campos para mostrar detalles relacionados
    estudios = EstudioSerializer(many=True, required=False)
    
    class Meta:
        model = Consulta
        fields = "__all__"
        depth = 1  # Para mostrar detalles relacionados

    def get_cita_descripcion(self, obj):
        if obj.cita:
            return f"Cita de {obj.cita.atleta.nombre} el {obj.cita.slot.fecha} a las {obj.cita.slot.hora_inicio}"
        return None

    def create(self, validated_data):
        estudios_data = validated_data.pop('estudios', [])
        consulta = Consulta.objects.create(**validated_data)
        
        for estudio_data in estudios_data:
            Estudio.objects.create(consulta=consulta, **estudio_data)
        
        return consulta

    def update(self, instance, validated_data):
        estudios_data = validated_data.pop('estudios', None)
        
        # Actualizar campos de consulta
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Manejo de estudios (actualización condicional)
        if estudios_data is not None:
            # Eliminar estudios no incluidos en la solicitud
            estudio_ids = [e.get('id') for e in estudios_data if e.get('id')]
            instance.estudios.exclude(id__in=estudio_ids).delete()
            
            # Crear o actualizar estudios
            for estudio_data in estudios_data:
                estudio_id = estudio_data.get('id', None)
                if estudio_id:
                    estudio = Estudio.objects.get(id=estudio_id, consulta=instance)
                    for attr, value in estudio_data.items():
                        setattr(estudio, attr, value)
                    estudio.save()
                else:
                    Estudio.objects.create(consulta=instance, **estudio_data)
        
        return instance


""" asignacion de programas de entrenamiento a atletas"""
class ProgramaAsignadoSerializer(serializers.ModelSerializer):
    atleta_nombre = serializers.CharField(source='atleta.__str__', read_only=True)
    programa_nombre = serializers.CharField(source='programa.nombre', read_only=True)

    class Meta:
        model = ProgramaAsignado
        fields = ['id', 'programa', 'programa_nombre', 'atleta', 'atleta_nombre', 'fecha_asignacion', 'estado', 'notas']
