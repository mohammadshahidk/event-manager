from django.utils import timezone
from zoneinfo import ZoneInfo

class TimezoneMiddleware:
    """
    Activates timezone from request header 'Timezone'.
    Defaults to Asia/Kolkata if not provided or invalid.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_name = request.headers.get("Timezone") or "Asia/Kolkata"
        try:
            timezone.activate(ZoneInfo(tz_name))
        except Exception:
            timezone.deactivate()
        return self.get_response(request)
