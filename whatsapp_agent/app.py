"""FastAPI webhook server bridging WhatsApp Cloud API and Claude."""
import hashlib
import hmac
import logging

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response

from .claude_client import get_reply
from .config import settings
from .whatsapp_client import send_text_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_agent")

app = FastAPI()


@app.get("/webhook")
def verify_webhook(request: Request) -> Response:
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge", "")

    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    if not settings.whatsapp_app_secret:
        # No app secret configured (dev only) — skip verification.
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.whatsapp_app_secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    provided = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def _handle_incoming_message(sender: str, text: str) -> None:
    try:
        reply = get_reply(sender, text)
        send_text_message(sender, reply)
    except Exception:
        logger.exception("Failed to handle message from %s", sender)


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    raw_body = await request.body()
    if not _verify_signature(raw_body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") != "text":
                    continue
                sender = message["from"]
                text = message["text"]["body"]
                background_tasks.add_task(_handle_incoming_message, sender, text)

    return {"status": "ok"}
