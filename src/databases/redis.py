"""Cache related - pooling, repository."""
from fastapi import Depends
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from utils import redis_pool


async def redis_pool_acquer(pool: ConnectionPool = Depends(redis_pool)):
    """Goes as context."""
    client = Redis(connection_pool=pool)
    try:
        yield RedisRepo(client)
    finally:
        await client.close(close_connection_pool=False)


class RedisRepo:
    """Redis client and database abs."""

    def __init__(self, conn: Redis):
        """One per dependant."""
        self._conn = conn

    async def check_cache(self, metric: str) -> int:
        """Get not expired values."""
        value = await self._conn.get(metric)
        if value:
            return int(value.decode())

    async def set_expiring_cache(self, metric: str, ttl: int, value: float | int):
        """
        SET val EX tm wrapper.

        :param ttl - seconds to expire
        """
        await self._conn.setex(metric, ttl, value)
