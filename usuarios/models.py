from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from datetime import timedelta

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
    
    def is_valid(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        if self.used:
            return False
        
        # Token válido por 1 hora
        expiry_time = self.created_at + timedelta(hours=1)
        return timezone.now() < expiry_time
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.save()
    
    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.used else 'Activo'}"

# Create your models here.
