from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)
from .models import PasswordResetToken
from .services import MailerooService
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UserProfileView(APIView):
    """
    View to retrieve user profile information.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Return the profile information for the authenticated user.
        """
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined,
        }
        
        # Add user groups if needed
        groups = user.groups.values_list('name', flat=True)
        data['groups'] = list(groups)
        
        if groups:
            data['tipo_usuario'] = groups[0]  # o usar lógica más específica
        else:
            data['tipo_usuario'] = 'sin_grupo'
        
        return Response(data)
    

class CustomTokenObtainPairView(BaseTokenObtainPairView):
    """
    Custom TokenObtainPairView to include user type in the token response.
    """
    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refresh = RefreshToken.for_user(serializer.user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'tipo_usuario': data['tipo_usuario'],
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Vista para solicitar recuperación de contraseña
    """
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Invalidar tokens anteriores del usuario
                PasswordResetToken.objects.filter(
                    user=user, 
                    used=False
                ).update(used=True)
                
                # Crear nuevo token
                reset_token = PasswordResetToken.objects.create(user=user)
                
                # Enviar email
                email_sent = MailerooService.send_password_reset_email(email, reset_token)
                
                if email_sent:
                    logger.info(f"Token de recuperación creado para usuario {user.username}")
                else:
                    logger.error(f"Error al enviar email de recuperación para {email}")
                    
            except User.DoesNotExist:
                # Por seguridad, no revelamos si el email existe
                logger.warning(f"Intento de recuperación para email inexistente: {email}")
            
            # Siempre devolvemos éxito por seguridad
            return Response({
                'message': 'Si el correo electrónico está registrado, recibirás un enlace de recuperación.',
                'success': True
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Vista para confirmar y restablecer la contraseña
    """
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            reset_token = serializer.validated_data['reset_token']
            new_password = serializer.validated_data['password']
            
            try:
                # Cambiar la contraseña
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Marcar el token como usado
                reset_token.mark_as_used()
                
                # Invalidar todas las sesiones del usuario
                # Esto fuerza al usuario a hacer login nuevamente
                
                logger.info(f"Contraseña restablecida exitosamente para usuario {user.username}")
                
                return Response({
                    'message': 'Tu contraseña ha sido restablecida exitosamente.',
                    'success': True
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error al restablecer contraseña: {str(e)}")
                return Response({
                    'message': 'Error interno del servidor.',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetValidateTokenView(APIView):
    """
    Vista para validar si un token de recuperación es válido
    """
    
    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'valid': False,
                'message': 'Token requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if reset_token.is_valid():
                return Response({
                    'valid': True,
                    'message': 'Token válido',
                    'user_email': reset_token.user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'message': 'Token expirado o ya usado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PasswordResetToken.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)