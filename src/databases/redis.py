"""Cache related - pooling, repository."""
from fastapi import Depends
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from src.utils import redis_pool
# try:
# except ModuleNotFoundError:
#     from src.utils import redis_pool


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

    async def check_cache(self, metric: str) -> float:
        """Get not expired values."""
        value = await self._conn.get(metric)
        if value:
            return float(value.decode())

    async def set_expiring_cache(self, metric: str, ttl: int, value: float | int):
        """
        SET val EX tm wrapper.

        :param ttl - seconds to expire
        """
        await self._conn.setex(metric, ttl, value)

    async def zset_add(self, zset: str, mapping: dict):
        """Store mapping as sorted by float."""
        await self._conn.zadd(zset, mapping=mapping)

    async def get_zset(self, set_name: str) -> dict[str, float]:
        """Use for distribution views."""
        scores = await self._conn.zscan(set_name)
        if scores:
            return {k.decode(): v for k, v in scores[1]}
