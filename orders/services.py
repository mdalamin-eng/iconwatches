from .models import Order
from notifications.services import notify_repeat_ip_after_cancel


def check_repeat_ip_after_cancel(new_order):
    """If this IP previously had a cancelled order, alert admin/manager.
    Called right after a new Order is created.
    """
    if not new_order.ip_address:
        return

    has_prior_cancellation = (
        Order.objects.filter(ip_address=new_order.ip_address, status=Order.Status.CANCELLED)
        .exclude(pk=new_order.pk)
        .exists()
    )
    if has_prior_cancellation:
        notify_repeat_ip_after_cancel(order=new_order)
