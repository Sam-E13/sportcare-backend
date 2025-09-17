from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('cita_confirmada', 'Cita Confirmada'),
        ('cita_cancelada', 'Cita Cancelada'),
        ('cita_reagendada', 'Cita Reagendada'),
        ('mensaje', 'Mensaje'),
        ('otro', 'Otro'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro')
    leida = models.BooleanField(default=False)
    creada_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.user.username}: {self.titulo}"

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"