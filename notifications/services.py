from .models import NotificationSettings, NotificationEvent
from .senders import send_telegram_message, send_whatsapp_message


def _dispatch(event_type, message, link=""):
    """Create the in-app popup event, then fan out to Telegram/WhatsApp
    if enabled in settings. Kept synchronous for simplicity - move to a
    Celery task if the API calls start slowing down requests.
    """
    NotificationEvent.objects.create(event_type=event_type, message=message, link=link)

    settings_obj = NotificationSettings.load()
    send_telegram_message(settings_obj, message)
    send_whatsapp_message(settings_obj, message)


def notify_product_viewed(product, ip_address=None):
    settings_obj = NotificationSettings.load()
    if not settings_obj.notify_on_product_view:
        return
    message = f"Customer viewed: {product.name}" + (f" (IP {ip_address})" if ip_address else "")
    _dispatch(
        NotificationEvent.EventType.PRODUCT_VIEW,
        message,
        link=product.get_absolute_url(),
    )


def notify_new_order(order):
    settings_obj = NotificationSettings.load()
    if not settings_obj.notify_on_new_order:
        return
    message = f"New order {order.order_number} from {order.full_name} ({order.phone})"
    _dispatch(NotificationEvent.EventType.NEW_ORDER, message)


def notify_repeat_ip_after_cancel(order):
    settings_obj = NotificationSettings.load()
    if not settings_obj.notify_on_repeat_ip_after_cancel:
        return
    message = (
        f"⚠ Order {order.order_number} placed from an IP ({order.ip_address}) "
        f"that previously had a cancelled order. Phone: {order.phone}"
    )
    _dispatch(NotificationEvent.EventType.REPEAT_IP_CANCEL, message)
