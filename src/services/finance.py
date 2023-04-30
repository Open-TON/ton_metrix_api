from fastapi import Depends

from databases.redis import redis_pool_acquer
from databases.redis import RedisRepo
from models.fins import CacheMetricsUSD


async def finance_header(cache: RedisRepo = Depends(redis_pool_acquer)) -> dict:
    return {
        'price': await cache.check_cache(CacheMetricsUSD.CURRENT_PRICE.value),
        'price_change_perc': await cache.check_cache(
            CacheMetricsUSD.PRICE_CHANGE_24H_PERC.value),
        'price_change': await cache.check_cache(CacheMetricsUSD.PRICE_CHANGE_24H.value),
        'market_cap': await cache.check_cache(CacheMetricsUSD.CURRENT_MARKET_CAP.value),
        'market_cap_change_perc': await cache.check_cache(
            CacheMetricsUSD.MARKET_CAP_CHANGE_24H_PERC.value),
        'volume': await cache.check_cache(CacheMetricsUSD.CURRENT_VOLUME.value),
        'volume_change_perc_24h': await cache.check_cache(
            CacheMetricsUSD.VOLUME_CHANGE_24H_PERC.value)
    }
