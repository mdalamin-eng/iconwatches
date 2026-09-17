from django.contrib import admin
from .models import NotificationSettings, NotificationEvent


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Singleton row - block creating a second one from django-admin
        return not NotificationSettings.objects.exists()


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "message", "is_read", "created_at")
    list_filter = ("event_type", "is_read")
