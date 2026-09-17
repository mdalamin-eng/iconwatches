from django.http import JsonResponse
from django.views.decorators.http import require_GET
from accounts.decorators import staff_required
from .models import NotificationEvent


@staff_required
@require_GET
def poll_notifications(request):
    """Polled every few seconds by dashboard JS.
    ?since=<last_seen_event_id> - returns only newer events.
    """
    since_id = int(request.GET.get("since", 0))
    events = NotificationEvent.objects.filter(id__gt=since_id).order_by("id")[:50]
    data = [
        {
            "id": e.id,
            "type": e.event_type,
            "message": e.message,
            "link": e.link,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
    latest_id = data[-1]["id"] if data else since_id
    return JsonResponse({"events": data, "latest_id": latest_id})
