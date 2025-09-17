from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register(r'Deportes', DeporteViewSet)
router.register(r'Profesionales-Salud', ProfesionalSaludViewSet)
router.register(r'Atletas', AtletaViewSet)
router.register(r'Categorias', CategoriaViewSet)
router.register(r'Consultorios', ConsultorioViewSet)
router.register(r'Areas', AreaViewSet)
router.register(r'Horarios', HorarioViewSet)
router.register(r'Usuarios', UserViewSet)
router.register(r'Citas-Disponibles', SlotsDisponiblesViewSet)
router.register(r'Disponibilidad-Temporal', DisponibilidadTemporalViewSet)
router.register(r'Entrenadores', EntrenadorViewSet)
router.register(r'Programas-Entrenamiento', ProgramaEntrenamientoViewSet)
router.register(r'Sesiones-Entrenamiento', SesionEntrenamientoViewSet)
router.register(r'Ejercicios', EjercicioViewSet)
router.register(r'GruposDeportivos', GrupoDeportivoViewSet)
router.register(r'metodologos', MetodologoViewSet)



urlpatterns = [
    path('', include(router.urls)), 
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('Atleta/<int:pk>/contacto/', atleta_contacto, name='atleta-contacto'),
    path('Entrenador/<int:pk>/', EntrenadorViewSet.as_view({'get': 'retrieve'}), name='entrenador-detalle'),
    path('api/responsables/atleta/<int:atleta_id>/', 
         ResponsableAtletaList.as_view(),
         name='responsables-atleta-list'),
    
    # Eliminar responsable específico
    path('api/responsables/<int:id>/', 
         ResponsableDeleteView.as_view(),
         name='responsable-delete'),
    
   path('api/responsables/atleta/<int:atleta_id>/create/', 
         ResponsableAtletaCreateView.as_view(), 
         name='responsable-atleta-create'),
   path('api/responsables/<int:pk>/update/',  # Añadimos /update/
         ResponsableUpdateAPIView.as_view(), 
         name='responsable-update'),
]