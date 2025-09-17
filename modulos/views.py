from rest_framework import viewsets, status
from django.http import HttpRequest, HttpResponse
from .models import *
from .serializers import *
from rest_framework.response import Response  
from django_filters.rest_framework import DjangoFilterBackend
import json

# Create your views here.
class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profesional_salud','atleta',]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            # Verificar disponibilidad del slot antes de guardar
            from .models import SlotDisponible
            slot_id = request.data.get('slot')
            
            try:
                slot = SlotDisponible.objects.get(id=slot_id)
                if not slot.disponible:
                    return Response(
                        {"detail": "Este horario ya no está disponible"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except SlotDisponible.DoesNotExist:
                return Response(
                    {"detail": "El horario seleccionado no existe"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['atleta', 'profesional_salud']

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Validar estudios
            estudios_data = []
            if 'estudios' in data:
                try:
                    estudios_data = json.loads(data['estudios'])
                    if not isinstance(estudios_data, list):
                        return Response(
                            {"message": "Los estudios deben ser una lista"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except json.JSONDecodeError:
                    return Response(
                        {"message": "El formato de los estudios es inválido"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Procesar archivos de estudios
            archivos_estudios = {}
            for key, file in request.FILES.items():
                if key.startswith('estudios_archivos_'):
                    try:
                        index = int(key.split('_')[-1])
                        archivos_estudios[index] = file
                    except (ValueError, IndexError):
                        continue
            
            # Crear consulta
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            consulta = serializer.instance
            
            # Crear estudios
            estudios_creados = []
            for index, estudio_data in enumerate(estudios_data):
                estudio_data['consulta'] = consulta.id
                if index in archivos_estudios:
                    estudio_data['archivo'] = archivos_estudios[index]
                
                estudio_serializer = EstudioSerializer(data=estudio_data)
                if estudio_serializer.is_valid():
                    estudio = estudio_serializer.save()
                    estudios_creados.append(estudio.id)
                else:
                    # Continuar pero registrar error
                    print(f"Error en estudio {index}: {estudio_serializer.errors}")
            
            # Incluir estudios en la respuesta
            response_data = serializer.data
            response_data['estudios_creados'] = estudios_creados
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            data = request.data.copy()

            # Validar disponibilidad del nuevo slot si cambia
            nuevo_slot_id = data.get('slot')
            if nuevo_slot_id and str(instance.slot_id) != str(nuevo_slot_id):
                from catalogos.models import SlotDisponible
                try:
                    nuevo_slot = SlotDisponible.objects.get(id=nuevo_slot_id)
                except SlotDisponible.DoesNotExist:
                    return Response({"detail": "El horario seleccionado no existe"}, status=status.HTTP_400_BAD_REQUEST)
                if not nuevo_slot.disponible:
                    return Response({"detail": "El nuevo horario ya no está disponible"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar estudios
            estudios_data = []
            if 'estudios' in data:
                try:
                    estudios_data = json.loads(data['estudios'])
                    if not isinstance(estudios_data, list):
                        return Response(
                            {"message": "Los estudios deben ser una lista"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except json.JSONDecodeError:
                    return Response(
                        {"message": "El formato de los estudios es inválido"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Procesar archivos de estudios
            archivos_estudios = {}
            for key, file in request.FILES.items():
                if key.startswith('estudios_archivos_'):
                    try:
                        index = int(key.split('_')[-1])
                        archivos_estudios[index] = file
                    except (ValueError, IndexError):
                        continue
            
            # Actualizar consulta
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            consulta = serializer.instance
            
            # Manejar estudios - eliminar todos los existentes y crear nuevos
            if estudios_data:
                # Eliminar estudios existentes
                consulta.estudios.all().delete()
                
                # Crear nuevos estudios
                estudios_creados = []
                for index, estudio_data in enumerate(estudios_data):
                    estudio_data['consulta'] = consulta.id
                    
                    # Agregar archivo si existe
                    if index in archivos_estudios:
                        estudio_data['archivo'] = archivos_estudios[index]
                    
                    # Remover campos que no deben ir al serializer
                    estudio_data.pop('archivo_url', None)  # Campo temporal del frontend
                    estudio_data.pop('isExisting', None)   # Campo temporal del frontend
                    
                    estudio_serializer = EstudioSerializer(data=estudio_data)
                    if estudio_serializer.is_valid():
                        estudio = estudio_serializer.save()
                        estudios_creados.append(estudio.id)
                    else:
                        print(f"Error en estudio {index}: {estudio_serializer.errors}")
            
            # Incluir estudios en la respuesta
            response_data = serializer.data
            if estudios_data:
                response_data['estudios_actualizados'] = len(estudios_creados)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
        
class EstudioViewSet(viewsets.ModelViewSet):
    queryset = Estudio.objects.all()
    serializer_class = EstudioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['consulta', 'tipo_estudio']


class ProgramaAsignadoViewSet(viewsets.ModelViewSet):
    queryset = ProgramaAsignado.objects.all()
    serializer_class = ProgramaAsignadoSerializer