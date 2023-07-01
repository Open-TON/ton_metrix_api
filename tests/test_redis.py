"""Cache storage checks."""
from asyncio import sleep
from types import NoneType

import pytest
from redis import asyncio

from src.config import main_config
from src.databases.redis import RedisRepo


@pytest.fixture(scope='module')
def redis_client():
    """Test connection provider."""
    redis = asyncio.Redis().from_url(main_config().cache.redis_url)
    # try:
    yield RedisRepo(redis)
    # finally:
    #     run(redis.close())


class TestRedis:
    """Redis operations."""

    METRIC_NAME = 'test'
    TEST_VAL = 7
    EXPIRATION_TIME_SEC = 1

    @pytest.mark.asyncio
    async def test_write(self, redis_client):
        """Store some `metric`."""
        setex = await redis_client.set_expiring_cache(
            self.METRIC_NAME, self.EXPIRATION_TIME_SEC,
            self.TEST_VAL)
        assert setex is None

    @pytest.mark.asyncio
    async def test_read(self, redis_client):
        """Easy reading."""
        readex = await redis_client.check_cache(self.METRIC_NAME)
        assert readex == self.TEST_VAL

    @pytest.mark.asyncio
    async def test_read_neg(self, redis_client):
        """Negative assertion."""
        readex = await redis_client.check_cache(self.METRIC_NAME)
        assert readex != self.TEST_VAL - 1

    @pytest.mark.asyncio
    async def test_read_expired(self, redis_client):
        """None right after ex time."""
        await sleep(self.EXPIRATION_TIME_SEC)
        readex = await redis_client.check_cache(self.METRIC_NAME)
        assert not readex

    @pytest.mark.asyncio
    async def test_get_zset(self, redis_client):
        """Data validation for national partitions."""
        res = await redis_client.get_zset('telegram_ton_chats')
        if type(res) not in (NoneType, dict):
            raise AssertionError
