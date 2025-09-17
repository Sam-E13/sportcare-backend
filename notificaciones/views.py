# views.py
from rest_framework import viewsets, permissions
from .serializers import NotificacionSerializer
from .models import Notificacion
from django_filters.rest_framework import DjangoFilterBackend

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'leida', 'user']

    