# serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import PasswordResetToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Acceder al usuario a través de self.user
        groups = self.user.groups.values_list('name', flat=True)
        
        if groups:
            data['tipo_usuario'] = groups[0]  
        else:
            data['tipo_usuario'] = 'sin_grupo'

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            pass
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        token = attrs.get('token')
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        # Verificar que las contraseñas coincidan
        if password != password_confirm:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        # Validar la contraseña con las reglas de Django
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        # Verificar que el token existe y es válido
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid():
                raise serializers.ValidationError("El token ha expirado o ya fue usado.")
            attrs['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        
        return attrs