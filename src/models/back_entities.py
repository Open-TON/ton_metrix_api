from pydantic.dataclasses import dataclass


@dataclass
class TelegramChat:
    """Telegram chat entry."""

    link: str
    language: str
    chat_type: str | None = None
    members: int = int()
