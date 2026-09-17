from django import forms
from notifications.models import NotificationSettings


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            "telegram_enabled", "telegram_bot_token", "telegram_chat_id",
            "whatsapp_enabled", "whatsapp_api_url", "whatsapp_api_token", "whatsapp_recipient_number",
            "notify_on_product_view", "notify_on_new_order", "notify_on_repeat_ip_after_cancel",
        ]
        widgets = {
            "telegram_bot_token": forms.TextInput(attrs={"class": "form-control"}),
            "telegram_chat_id": forms.TextInput(attrs={"class": "form-control"}),
            "whatsapp_api_url": forms.TextInput(attrs={"class": "form-control"}),
            "whatsapp_api_token": forms.TextInput(attrs={"class": "form-control"}),
            "whatsapp_recipient_number": forms.TextInput(attrs={"class": "form-control"}),
        }
