"""Sends outbound messages through the WhatsApp Cloud API (Meta Graph API)."""
import httpx

from .config import settings

GRAPH_API_VERSION = "v21.0"


def send_text_message(to: str, body: str) -> None:
    url = (
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body[:4096]},
    }
    response = httpx.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
