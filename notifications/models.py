from django.db import models


class NotificationSettings(models.Model):
    """Singleton-style row edited from the dashboard so admin can plug in
    API keys without touching code or redeploying.
    """
    telegram_enabled = models.BooleanField(default=False)
    telegram_bot_token = models.CharField(max_length=255, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)

    whatsapp_enabled = models.BooleanField(default=False)
    whatsapp_api_url = models.CharField(
        max_length=255, blank=True,
        help_text="e.g. https://graph.facebook.com/v19.0/<phone_number_id>/messages",
    )
    whatsapp_api_token = models.CharField(max_length=500, blank=True)
    whatsapp_recipient_number = models.CharField(max_length=20, blank=True)

    notify_on_product_view = models.BooleanField(default=True)
    notify_on_new_order = models.BooleanField(default=True)
    notify_on_repeat_ip_after_cancel = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification settings"
        verbose_name_plural = "Notification settings"

    def __str__(self):
        return "Notification settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NotificationEvent(models.Model):
    """Feed of in-app events for the admin/manager popup. The dashboard
    polls GET /api/notifications/poll/?since=<id> and marks events read.
    """
    class EventType(models.TextChoices):
        PRODUCT_VIEW = "product_view", "Product viewed"
        NEW_ORDER = "new_order", "New order"
        REPEAT_IP_CANCEL = "repeat_ip_cancel", "Repeat IP after cancellation"

    event_type = models.CharField(max_length=30, choices=EventType.choices)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.event_type}] {self.message}"
