from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from accounts.decorators import staff_required, admin_required
from orders.models import Order
from notifications.models import NotificationSettings, NotificationEvent
from .forms import NotificationSettingsForm


@staff_required
def home(request):
    stats = {
        "pending_orders": Order.objects.filter(status=Order.Status.PENDING).count(),
        "total_orders_today": Order.objects.filter(created_at__date=timezone.now().date()).count(),
        "cancelled_orders": Order.objects.filter(status=Order.Status.CANCELLED).count(),
    }
    recent_orders = Order.objects.all()[:10]
    return render(request, "dashboard/home.html", {"stats": stats, "recent_orders": recent_orders})


@staff_required
def order_list(request):
    status = request.GET.get("status")
    orders = Order.objects.all()
    if status:
        orders = orders.filter(status=status)
    return render(request, "dashboard/order_list.html", {"orders": orders, "statuses": Order.Status.choices})


@staff_required
def order_update_status(request, order_number):
    if request.method == "POST":
        order = Order.objects.get(order_number=order_number)
        new_status = request.POST.get("status")
        if new_status in Order.Status.values:
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Order {order_number} updated to {new_status}.")
    return redirect("dashboard:order_list")


@admin_required
def notification_settings(request):
    """Admin-only: plug in Telegram bot token / WhatsApp API credentials
    without touching code or redeploying.
    """
    settings_obj = NotificationSettings.load()
    if request.method == "POST":
        form = NotificationSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification settings saved.")
            return redirect("dashboard:notification_settings")
    else:
        form = NotificationSettingsForm(instance=settings_obj)
    return render(request, "dashboard/notification_settings.html", {"form": form})
