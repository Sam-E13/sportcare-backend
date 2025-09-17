from catalogos.servicios.Cita_Slot_Generator import eliminar_slots_disponibles
from django.utils import timezone
from django.core.cache import cache

class SlotCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ejecutar limpieza solo una vez cada 10 minutos
        cache_key = 'last_slot_cleanup'
        last_cleanup = cache.get(cache_key)
        now = timezone.now()
        
        if not last_cleanup or (now - last_cleanup).seconds > 600:  # 10 minutos
            eliminar_slots_disponibles()
            cache.set(cache_key, now, 600)  # Cache por 10 minutos
        
        response = self.get_response(request)
        return response