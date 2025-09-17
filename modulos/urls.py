# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'Citas', CitaViewSet)
router.register(r'Estudios', EstudioViewSet)
router.register(r'Consultas', ConsultaViewSet)
router.register(r'Asignacion-de-Programas-de-Entrenamiento', ProgramaAsignadoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]