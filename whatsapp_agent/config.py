"""Configuration loaded from environment variables (.env in local dev)."""
import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class Settings:
    def __init__(self) -> None:
        self.whatsapp_token = _require("WHATSAPP_TOKEN")
        self.whatsapp_phone_number_id = _require("WHATSAPP_PHONE_NUMBER_ID")
        self.whatsapp_verify_token = _require("WHATSAPP_VERIFY_TOKEN")
        self.whatsapp_app_secret = os.environ.get("WHATSAPP_APP_SECRET", "")
        self.anthropic_api_key = _require("ANTHROPIC_API_KEY")
        self.anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
        self.system_prompt = os.environ.get(
            "AGENT_SYSTEM_PROMPT",
            "You are a helpful assistant answering WhatsApp messages. Keep replies concise.",
        )


settings = Settings()
