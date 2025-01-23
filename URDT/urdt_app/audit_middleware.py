from .models import AuditLog
from django.utils.timezone import now

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=f"Accessed {request.path}",
                timestamp=now(),
                additional_info=f"Method: {request.method}"
            )
        return self.get_response(request)
