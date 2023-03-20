from redis.client import Redis

from fastapi import Depends
from redis.connection import ConnectionPool

from utils import get_redis_pool


def redis_pool_acquer(pool: ConnectionPool = Depends(get_redis_pool)):
    client = Redis(connection_pool=pool)
    try:
        yield RedisRepo(client)
    finally:
        client.close()


class RedisRepo:

    def __init__(self, conn: Redis):
        self._conn = conn

    def check_cache(self, metric: str) -> int:
        value = self._conn.get(metric)
        return int(value.decode())

    def set_cache(self, metric: str, ttl: int, value: int):
        self._conn.setex(metric, ttl, value)
