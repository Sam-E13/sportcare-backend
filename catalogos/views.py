import json
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView
from rest_framework.response import Response
import requests
from django.shortcuts import get_object_or_404
import re
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser

class DeporteViewSet(viewsets.ModelViewSet):
    queryset = Deporte.objects.all().select_related('grupo') 
    serializer_class = DeporteSerializer
    
class GrupoDeportivoViewSet(viewsets.ModelViewSet):
    queryset = GrupoDeportivo.objects.all()
    serializer_class = GrupoDeportivoSerializer
    
class MetodologoViewSet(viewsets.ModelViewSet):
    queryset = Metodologo.objects.all()
    serializer_class = MetodologoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros opcionales
        deporte_id = self.request.query_params.get('deporte_id')
        grupo_id = self.request.query_params.get('grupo_id') 
        
        if deporte_id:
            queryset = queryset.filter(deportes__id=deporte_id)
        if grupo_id:
            queryset = queryset.filter(grupos__id=grupo_id)
            
        return queryset
    
class AtletaViewSet(viewsets.ModelViewSet):
    queryset = Atleta.objects.all()
    serializer_class = AtletaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']  # Permite filtrar por user_id
    
@api_view(['GET', 'POST'])
def atleta_contacto(request, pk):
    try:
        if request.method == 'GET':
            try:
                contacto = AtletaContacto.objects.get(atleta_id=pk)
                serializer = AtletaContactoSerializer(contacto)
                return Response(serializer.data)
            except AtletaContacto.DoesNotExist:
                return Response(
                    {
                        'exists': False, 
                        'atleta_id': pk,
                        'telefono': '',
                        'email': '',
                        'calle': '',
                        'noExterior': '',
                        'noInterior': '',
                        'colonia': '',
                        'cp': '',
                        'ciudad': '',
                        'estado': '',
                        'pais': 'México'
                    },
                    status=status.HTTP_200_OK
                )

        elif request.method == 'POST':
            data = request.data.copy()
            data['atleta'] = pk
            
            try:
                contacto = AtletaContacto.objects.get(atleta_id=pk)
                serializer = AtletaContactoSerializer(contacto, data=data)
            except AtletaContacto.DoesNotExist:
                serializer = AtletaContactoSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )   

class ResponsableAtletaList(ListAPIView):
    """
    Vista para listar todos los responsables de un atleta
    """
    serializer_class = ResponsableAtletaSerializer
    
    def get_queryset(self):
        atleta_id = self.kwargs['atleta_id']
        return ResponsableAtleta.objects.filter(atleta_id=atleta_id)

class ResponsableDeleteView(DestroyAPIView):
    """
    Vista para eliminar un responsable específico
    """
    queryset = ResponsableAtleta.objects.all()
    serializer_class = ResponsableAtletaSerializer
    lookup_field = 'id'  # Usamos el campo id como identificador
    
    def perform_destroy(self, instance):
        # Opcional: puedes agregar lógica adicional antes de eliminar
        super().perform_destroy(instance)

class ResponsableAtletaCreateView(APIView):
    def post(self, request, atleta_id):
        try:
            atleta = Atleta.objects.get(pk=atleta_id)
        except Atleta.DoesNotExist:
            return Response(
                {"detail": "Atleta no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crea copia mutable de los datos sin 'atleta'
        data = request.data.copy()
        if 'atleta' in data:
            del data['atleta']

        serializer = ResponsableAtletaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(atleta=atleta)  # ← Asigna el atleta aquí
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        # Debug: Imprime errores en consola
        print("Errores del serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResponsableUpdateAPIView(generics.UpdateAPIView):
    queryset = ResponsableAtleta.objects.all()
    serializer_class = ResponsableAtletaSerializer
    

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ConsultorioViewSet(viewsets.ModelViewSet):
    queryset = Consultorio.objects.all()
    serializer_class = ConsultorioSerializer

class ProfesionalSaludViewSet(viewsets.ModelViewSet):
    queryset = ProfesionalSalud.objects.all()
    serializer_class = ProfesionalSaludSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']  # Esto permite filtrar por user_id

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        print("Username recibido:", username)
        print("Password recibido:", password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all().select_related('profesional_salud', 'consultorio')
    serializer_class = HorarioSerializer

class SlotsDisponiblesViewSet(viewsets.ModelViewSet):
    queryset = SlotDisponible.objects.all().select_related('profesional_salud', 'consultorio', 'area')
    serializer_class = SlotDisponibleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'profesional_salud': ['exact'],
        'consultorio': ['exact'], 
        'area': ['exact'],
        'fecha': ['exact', 'gte', 'lte'],
        'hora_inicio': ['exact', 'gte', 'lt', 'lte'],
        'hora_fin': ['exact', 'gte', 'lt', 'lte'],
        'disponible': ['exact'],
    }

class DisponibilidadTemporalViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadTemporal.objects.all().select_related('profesional_salud', 'consultorio')
    serializer_class = DisponibilidadTemporalSerializer
    
class EntrenadorViewSet(viewsets.ModelViewSet):
    queryset = Entrenador.objects.all()
    serializer_class = EntrenadorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']  # Permite filtrar por user_id
        
class ProgramaEntrenamientoViewSet(viewsets.ModelViewSet):
    queryset = ProgramaEntrenamiento.objects.all().prefetch_related('sesiones__ejercicios')
    serializer_class = ProgramaEntrenamientoSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entrenador']
    
    def get_serializer_context(self):
        """Asegurar que el contexto de request se pase al serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # --- MÉTODO CORREGIDO ---
    def create(self, request, *args, **kwargs):
        
        # Convertimos el QueryDict de POST a un dict estándar de Python
        data = request.POST.dict()
        
        # Decodificamos la cadena JSON de 'sesiones' si existe
        if 'sesiones' in data and isinstance(data['sesiones'], str):
            try:
                data['sesiones'] = json.loads(data['sesiones'])
                print(f"  Sesiones parsed: {data['sesiones']}")
            except json.JSONDecodeError as e:
                print(f"  JSON decode error: {e}")
                return Response({'sesiones': ['Formato de sesiones inválido.']}, status=status.HTTP_400_BAD_REQUEST)

        # --- CORRECCIÓN CLAVE PARA EL ARCHIVO ---
        # Asignamos el archivo directamente para evitar que se envuelva en una lista.
        # request.FILES.get('archivo') devuelve el objeto de archivo o None.
        if 'archivo' in request.FILES:
            data['archivo'] = request.FILES.get('archivo')

        # Pasamos el diccionario limpio al serializador
        serializer = self.get_serializer(data=data)
        
        # Validamos y si hay errores, los devolvemos (con tu log)
        if not serializer.is_valid():
            print(f"  Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Si la validación es exitosa, creamos el objeto
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Método personalizado para actualizar programas con sesiones"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Convertimos el QueryDict de POST a un dict estándar de Python
        data = request.POST.dict() if hasattr(request, 'POST') else request.data.copy()
        
        # Decodificamos la cadena JSON de 'sesiones' si existe
        if 'sesiones' in data and isinstance(data['sesiones'], str):
            try:
                data['sesiones'] = json.loads(data['sesiones'])
                print(f"  UPDATE - Sesiones parsed: {data['sesiones']}")
            except json.JSONDecodeError as e:
                print(f"  UPDATE - JSON decode error: {e}")
                return Response({'sesiones': ['Formato de sesiones inválido.']}, status=status.HTTP_400_BAD_REQUEST)

        # Manejo del archivo
        if 'archivo' in request.FILES:
            data['archivo'] = request.FILES.get('archivo')

        serializer = self.get_serializer(instance, data=data, partial=partial)
        
        if not serializer.is_valid():
            print(f"  UPDATE - Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response(serializer.data)


class SesionEntrenamientoViewSet(viewsets.ModelViewSet):
    queryset = SesionEntrenamiento.objects.all()
    serializer_class = SesionEntrenamientoSerializer


class EjercicioViewSet(viewsets.ModelViewSet):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer


