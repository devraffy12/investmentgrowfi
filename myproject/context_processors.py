from django.conf import settings
from .models import Notification


def notification_count(request):
    """Context processor to add unread notification count."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
        return {"unread_notifications_count": unread_count}
    return {"unread_notifications_count": 0}


def firebase_client_config(request):
    """Expose Firebase client config to templates as FIREBASE_CLIENT_CONFIG."""
    config = getattr(settings, "FIREBASE_CLIENT_CONFIG", None)
    # Ensure it renders as JSON object in templates
    return {"FIREBASE_CLIENT_CONFIG": config}
