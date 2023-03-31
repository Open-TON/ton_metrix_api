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
