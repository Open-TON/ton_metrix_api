from pydantic.dataclasses import dataclass


@dataclass
class TelegramChat:
    """Telegram chat entry."""

    link: str
    language: str
    chat_type: str | None = None
    members: int = int()


DEVIATION_MAPPING = {
    60 * 60: .2,
    5 * 60: .3,
    60 * 60 * 24: 0
}
