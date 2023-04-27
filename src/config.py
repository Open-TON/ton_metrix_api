"""Config data management."""
import configparser

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DBConfig:
    """Analytics database."""

    dsn: str
    db_name: str


@dataclass(frozen=True)
class CacheConfig:
    """Cache service."""

    redis_url: str


@dataclass(frozen=True)
class MainConfig:
    """Whole data."""

    db: DBConfig
    cache: CacheConfig


def read_config(ini_path: str) -> MainConfig:
    """Config factory."""
    config = configparser.ConfigParser()
    config.read(ini_path)

    db = config['database']
    cache = config['cache']

    return MainConfig(
        DBConfig(db.get('MONGO_URI'), db.get('DATABASE_NAME')),
        CacheConfig(cache.get('REDIS_DSN'))
    )


@dataclass(frozen=True)
class TelegramApiConfig:
    """Telegram userbot settings."""

    api_id: int
    api_hash: str


def read_tg_client_conf(config_path: str) -> TelegramApiConfig:
    """Inject API parameters."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_path)

    tg_api = config_parser['telegram_api']

    return TelegramApiConfig(
        tg_api.get('API_ID'),
        tg_api.get('API_HASH')
    )
