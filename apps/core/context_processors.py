from django.conf import settings
from django.utils import timezone


def tenant_context(request):
    return {
        'current_tenant': getattr(request, 'tenant', None),
        'app_name': getattr(settings, 'APP_NAME', 'NavHRM'),
        # D-15: templates compare expiry/due dates against `today`; previously undefined.
        'today': timezone.localdate(),
    }
