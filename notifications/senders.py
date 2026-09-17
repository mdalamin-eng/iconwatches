import logging
import requests

logger = logging.getLogger(__name__)


def send_telegram_message(settings_obj, text):
    if not (settings_obj.telegram_enabled and settings_obj.telegram_bot_token and settings_obj.telegram_chat_id):
        return False
    url = f"https://api.telegram.org/bot{settings_obj.telegram_bot_token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": settings_obj.telegram_chat_id, "text": text},
            timeout=5,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Telegram notification failed")
        return False


def send_whatsapp_message(settings_obj, text):
    """Uses the WhatsApp Business Cloud API shape:
    POST {whatsapp_api_url} with Bearer token, sends a text message to
    whatsapp_recipient_number. Swap the payload shape here if you use a
    different provider (Twilio, etc).
    """
    if not (settings_obj.whatsapp_enabled and settings_obj.whatsapp_api_url
            and settings_obj.whatsapp_api_token and settings_obj.whatsapp_recipient_number):
        return False
    headers = {
        "Authorization": f"Bearer {settings_obj.whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings_obj.whatsapp_recipient_number,
        "type": "text",
        "text": {"body": text},
    }
    try:
        resp = requests.post(settings_obj.whatsapp_api_url, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("WhatsApp notification failed")
        return False
