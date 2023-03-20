import configparser

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DBConfig:
    dsn: str
    db_name: str


@dataclass(frozen=True)
class CacheConfig:
    redis_url: str


@dataclass(frozen=True)
class MainConfig:
    db: DBConfig
    cache: CacheConfig


def read_config(ini_path: str) -> MainConfig:
    config = configparser.ConfigParser()
    config.read(ini_path)

    db = config['database']
    cache = config['cache']

    return MainConfig(
        DBConfig(db.get('MONGO_URI'), db.get('DATABASE_NAME')),
        CacheConfig(cache.get('REDIS_DSN'))
    )
