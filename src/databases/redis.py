"""Cache related - pooling, repository."""
from fastapi import Depends
from redis.client import Redis
from redis.connection import ConnectionPool

from utils import redis_pool


def redis_pool_acquer(pool: ConnectionPool = Depends(redis_pool)):
    """Goes as context."""
    client = Redis(connection_pool=pool)
    try:
        yield RedisRepo(client)
    finally:
        client.close()


class RedisRepo:
    """Redis client and database abs."""

    def __init__(self, conn: Redis):
        """One per dependant."""
        self._conn = conn

    def check_cache(self, metric: str) -> int:
        """Get not expired values."""
        value = self._conn.get(metric)
        if value:
            return int(value.decode())

    def set_cache(self, metric: str, ttl: int, value: int):
        """SET val EX tm wrapper."""
        self._conn.setex(metric, ttl, value)
