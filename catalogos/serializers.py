from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()


class DeporteSerializer(serializers.ModelSerializer):
    grupo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Deporte
        fields = ['id', 'nombre', 'grupo', 'grupo_display']
    
    def get_grupo_display(self, obj):
        return obj.grupo.nombre if obj.grupo else None
    
class GrupoDeportivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoDeportivo
        fields = ['id', 'nombre', 'descripcion']

class MetodologoSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    grupos_display = serializers.SerializerMethodField()
    deportes_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Metodologo
        fields = ['id', 'user', 'user_display', 'nombre', 'aPaterno', 'aMaterno', 
                 'grupos', 'grupos_display', 'deportes', 'deportes_display']
    
    def get_user_display(self, obj):
        return obj.user.username if obj.user else None
    
    def get_grupos_display(self, obj):
        return [grupo.nombre for grupo in obj.grupos.all()]
    
    def get_deportes_display(self, obj):
        return [deporte.nombre for deporte in obj.deportes.all()]
    
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class AtletaSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    categorias = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        allow_null=True,
        required=False
    )
    # Para mostrar el nombre de la categoría
    categorias_display = serializers.SerializerMethodField()
    
    # Para mostrar los nombres de los deportes en el listado
    deportes_display = serializers.SerializerMethodField()
    
    # Para la edición (mantener los IDs)
    deportes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Deporte.objects.all(),
        required=False
    )

    class Meta:
        model = Atleta
        fields = '__all__'

    def get_categorias_display(self, obj):
        if obj.categorias:
            return obj.categorias.nombre
        return "No especificado"
        
    def get_deportes_display(self, obj):
        return ", ".join([deporte.nombre for deporte in obj.deportes.all()]) or "No especificado"
    
class AtletaUpdateSerializer(serializers.ModelSerializer):
    deportes = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Deporte.objects.all()
    )
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all()
    )
    programa_actual = serializers.SerializerMethodField() 

    class Meta:
        model = Atleta
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'curp': {'read_only': True},
            'rfc': {'read_only': True}
        }
        

class AtletaContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtletaContacto
        fields = '__all__'
        extra_kwargs = {
            'atleta': {'required': True},
            'telefono': {'required': True},
            'email': {'required': True},
            'calle': {'required': True},
            'colonia': {'required': True},
            'cp': {'required': True},
            'ciudad': {'required': True},
            'estado': {'required': True},
            'pais': {'required': True}
        }

class ResponsableAtletaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsableAtleta
        fields = ['id', 'atleta', 'nombre', 'parentesco', 'telefono']
        read_only_fields = ['atleta']  # ← Esto es clave
        extra_kwargs = {
            'nombre': {'required': True},
            'parentesco': {'required': True},
            'telefono': {'required': True}
        }
        

class ConsultorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultorio
        fields = '__all__'

class ProfesionalSaludSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesionalSalud
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ['id', 'username']  # Solo campos necesarios
        

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Opcional: limpiar el username si es necesario
        data['username'] = data['username'].strip().replace('()', '')
        return data

class HorarioSerializer(serializers.ModelSerializer):
    # Campos para insersion y actualizacion de datos
    profesional_salud = serializers.PrimaryKeyRelatedField(queryset=ProfesionalSalud.objects.all())
    consultorio = serializers.PrimaryKeyRelatedField(queryset=Consultorio.objects.all())
    
    # Campos de solo lectura para mostrar la información relacionada
    profesional_salud_nombre = serializers.CharField(source='profesional_salud.nombre', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    
    class Meta:
        model = Horario
        fields = '__all__'

    def validate(self, data):
        if data['hora_inicio'] >= data['hora_fin']:
            raise serializers.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        return data
    

class SlotDisponibleSerializer(serializers.ModelSerializer):
    #campos para insersion y actualizacion de datos
    profesional_salud = serializers.PrimaryKeyRelatedField(queryset=ProfesionalSalud.objects.all())
    consultorio = serializers.PrimaryKeyRelatedField(queryset=Consultorio.objects.all())
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())

    # Campos para lectura y mostracion de datos
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    profesional_salud_nombre = serializers.CharField(source='profesional_salud.nombre', read_only=True)
    
    class Meta:
        model = SlotDisponible
        fields = "__all__"


class DisponibilidadTemporalSerializer(serializers.ModelSerializer):
    # Campos para insersion y actualizacion de datos
    profesional_salud = serializers.PrimaryKeyRelatedField(queryset=ProfesionalSalud.objects.all())
    consultorio = serializers.PrimaryKeyRelatedField(queryset=Consultorio.objects.all())
    
    # Campos de solo lectura para mostrar la información relacionada
    profesional_salud_nombre = serializers.CharField(source='profesional_salud.nombre', read_only=True)
    consultorio_nombre = serializers.CharField(source='consultorio.nombre', read_only=True)
    
    class Meta:
        model = DisponibilidadTemporal
        fields = '__all__'

""" aaqui comienzan los serializers para los programas de entrenamiento """
class EntrenadorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    # Para mostrar los nombres de las disciplinas en el listado
    disciplinas_display = serializers.SerializerMethodField()
    
    # Para la edición (mantener los IDs)
    disciplinas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Deporte.objects.all(),
        required=False
    )

    class Meta:
        model = Entrenador
        fields = '__all__'
        
    def get_disciplinas_display(self, obj):
        return ", ".join([disciplina.nombre for disciplina in obj.disciplinas.all()]) or "No especificado"


class EntrenadorUpdateSerializer(serializers.ModelSerializer):
    disciplinas = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Deporte.objects.all()
    )
    
    class Meta:
        model = Entrenador
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
        
class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = [
            'id', 
            'nombre', 
            'repeticiones', 
            'series', 
            'duracion_segundos',
            'distancia_metros', 
            'peso_kg', 
            'observaciones'
        ]

### --- SERIALIZADOR DE SESION CON SUS EJERCICIOS ---
class SesionEntrenamientoSerializer(serializers.ModelSerializer):
    ejercicios = EjercicioSerializer(many=True)

    class Meta:
        model = SesionEntrenamiento
        fields = ['dia', 'titulo', 'descripcion', 'ejercicios']

    def create(self, validated_data):
        ejercicios_data = validated_data.pop('ejercicios')
        sesion = SesionEntrenamiento.objects.create(**validated_data)
        for ejercicio_data in ejercicios_data:
            Ejercicio.objects.create(sesion=sesion, **ejercicio_data)
        return sesion


### --- SERIALIZADOR DE PROGRAMA CON SESIONES Y EJERCICIOS ---
class ProgramaEntrenamientoSerializer(serializers.ModelSerializer):
    # Campos para escritura (crear/actualizar)
    entrenador = serializers.PrimaryKeyRelatedField(queryset=Entrenador.objects.all())
    deporte = serializers.PrimaryKeyRelatedField(queryset=Deporte.objects.all())
    
    # Campos adicionales de solo lectura para mostrar nombres
    entrenador_nombre = serializers.SerializerMethodField(read_only=True)
    deporte_nombre = serializers.CharField(source='deporte.nombre', read_only=True)
    archivo_url = serializers.SerializerMethodField(read_only=True)
    
    # CORRECCIÓN: Removemos write_only=True para que las sesiones se incluyan en GET
    sesiones = SesionEntrenamientoSerializer(many=True, required=False)

    class Meta:
        model = ProgramaEntrenamiento
        fields = [
            'id', 'nombre', 'descripcion', 'deporte', 'deporte_nombre', 'nivel', 'objetivo',
            'duracion_dias', 'entrenador', 'entrenador_nombre', 'archivo', 'archivo_url', 'sesiones'
        ]
    
    def get_entrenador_nombre(self, obj):
        """Método para obtener el nombre completo del entrenador"""
        if obj.entrenador:
            return f"{obj.entrenador.nombre} {obj.entrenador.apPaterno} {obj.entrenador.apMaterno}"
        return "No especificado"
    
    def get_archivo_url(self, obj):
        """Método para obtener la URL completa del archivo"""
        if obj.archivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None
        
    def to_representation(self, instance):
        """Personalizar la representación para incluir sesiones con ejercicios"""
        data = super().to_representation(instance)
        
        # Obtener las sesiones con sus ejercicios
        sesiones = instance.sesiones.all().prefetch_related('ejercicios')
        data['sesiones'] = SesionEntrenamientoSerializer(sesiones, many=True).data
        
        return data

    def create(self, validated_data):
        sesiones_data = validated_data.pop('sesiones', [])
        programa = ProgramaEntrenamiento.objects.create(**validated_data)
        for sesion_data in sesiones_data:
            ejercicios_data = sesion_data.pop('ejercicios')
            sesion = SesionEntrenamiento.objects.create(programa=programa, **sesion_data)
            for ejercicio_data in ejercicios_data:
                Ejercicio.objects.create(sesion=sesion, **ejercicio_data)
        return programa

    def update(self, instance, validated_data):
        """Método para actualizar programa con sesiones"""
        sesiones_data = validated_data.pop('sesiones', [])
        
        # Actualizar campos del programa
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Eliminar sesiones existentes y crear nuevas
        instance.sesiones.all().delete()
        for sesion_data in sesiones_data:
            ejercicios_data = sesion_data.pop('ejercicios')
            sesion = SesionEntrenamiento.objects.create(programa=instance, **sesion_data)
            for ejercicio_data in ejercicios_data:
                Ejercicio.objects.create(sesion=sesion, **ejercicio_data)
        
        return instance

""" aqui termian los serializers para programas de entrenamiento """