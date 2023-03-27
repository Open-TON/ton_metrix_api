"""Cache storage checks."""
import time as tm

import pytest
from redis.client import Redis

from databases.redis import RedisRepo


@pytest.fixture
def redis_client():
    """Test connection provider."""
    redis = Redis()
    try:
        yield RedisRepo(redis)
    finally:
        redis.close()


class TestRedis:
    """Redis operations."""

    METRIC_NAME = 'test'
    TEST_VAL = 7
    EXPIRATION_TIME_SEC = 1

    def test_write(self, redis_client):
        """Store some `metric`."""
        setex = redis_client.set_cache(
            self.METRIC_NAME, self.EXPIRATION_TIME_SEC,
            self.TEST_VAL)
        assert setex is None

    def test_read(self, redis_client):
        """Easy reading."""
        readex = redis_client.check_cache(self.METRIC_NAME)
        assert readex == self.TEST_VAL

    def test_read_neg(self, redis_client):
        """Negative assertion."""
        readex = redis_client.check_cache(self.METRIC_NAME)
        assert readex != self.TEST_VAL - 1

    def test_read_expired(self, redis_client):
        """None right after ex time."""
        tm.sleep(self.EXPIRATION_TIME_SEC)
        readex = redis_client.check_cache(self.METRIC_NAME)
        assert not readex
