
from django.urls import path
from .views import *


urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/validate/', PasswordResetValidateTokenView.as_view(), name='password_reset_validate'),
]

