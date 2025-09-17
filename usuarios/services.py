# services.py (versión mejorada para diagnóstico)

import logging
import requests
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import PasswordResetToken

logger = logging.getLogger(__name__)

class MailerooService:
    API_URL = "https://smtp.maileroo.com/api/v2/emails"

    @staticmethod
    def send_password_reset_email(user_email, reset_token):
        try:
            user = User.objects.get(email=user_email)
            
            # URL del enlace de recuperación
            reset_url = f"{settings.FRONTEND_URL}/restablecer-password?token={reset_token.token}"
            
            # Contexto para el template
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'SportCare IDET',
                'valid_hours': 1,
            }
            
            # Renderizar el template HTML
            html_content = render_to_string('emails/password_reset.html', context)
            text_content = strip_tags(html_content)
            
            # PAYLOAD CORREGIDO según la documentación de Maileroo
            payload = {
                "from": {
                    "address": settings.EMAIL_HOST_USER,
                    "display_name": "SportCare IDET"
                },
                "to": [
                    {
                        "address": user_email,
                        "display_name": f"{user.first_name} {user.last_name}".strip() or user.username
                    }
                ],
                "subject": "Recuperación de Contraseña - SportCare IDET",
                "html": html_content,
                "plain": text_content,
                "tracking": True
            }
            
            # Headers corregidos
            headers = {
                "Authorization": f"Bearer {settings.EMAIL_HOST_PASSWORD}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"Enviando email a {user_email} usando Maileroo API")
            logger.debug(f"Payload: {payload}")
            
            # Enviar el email
            response = requests.post(
                MailerooService.API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Respuesta de Maileroo: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email de recuperación enviado exitosamente a {user_email}")
                return True
            else:
                logger.error(f"Error al enviar email: {response.status_code} - {response.text}")
                return False
                
        except User.DoesNotExist:
            logger.warning(f"Intento de recuperación para email inexistente: {user_email}")
            return True  # Por seguridad, siempre devolvemos True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a Maileroo: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Respuesta de Maileroo (código {e.response.status_code}): {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {str(e)}")
            return False