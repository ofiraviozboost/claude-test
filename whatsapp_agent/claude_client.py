"""Wraps the Anthropic Messages API and keeps a short per-sender history."""
import collections
import threading

import anthropic

from .config import settings

MAX_TURNS_PER_SENDER = 20

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
_lock = threading.Lock()
_history: dict[str, collections.deque] = collections.defaultdict(
    lambda: collections.deque(maxlen=MAX_TURNS_PER_SENDER)
)


def get_reply(sender_id: str, user_text: str) -> str:
    with _lock:
        history = _history[sender_id]
        history.append({"role": "user", "content": user_text})
        messages = list(history)

    response = _client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=settings.system_prompt,
        messages=messages,
    )
    reply_text = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    with _lock:
        _history[sender_id].append({"role": "assistant", "content": reply_text})

    return reply_text or "מצטער, לא הצלחתי לייצר תשובה כרגע."
