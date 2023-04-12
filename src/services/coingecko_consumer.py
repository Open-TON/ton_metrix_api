"""Big analytics player API client."""
import datetime as dt
from enum import Enum

from aiohttp import ClientSession
from fastapi import Depends

from databases.redis import redis_pool_acquer, RedisRepo

class GeckoCoinIDs(Enum):
    """Coingecko coin IDs from and for their API."""

class GeckoClient:
    """Talks to """
    
    GECKO_TON_ID = 'the-open-network'
    
    def __init__(self, cache=Depends(redis_pool_acquer)):
        self.cache: RedisRepo = cache

    async def query_coin(self):
        """
        Financial data.

        The most part. Runs once in a day.
        """
        async with ClientSession('https://api.coingecko.com') as aio_cli:
            async with aio_cli.get(f'/api/v3/coins/{self.GECKO_TON_ID}?tickers=false&'
                                   f'developer_data=false&sparkline=false') as resp:
                data = await resp.json()
        flow = {
            'price_usd': data['market_data']['current_price']['usd'],
            'h24_usd': data['market_data']['high_24h']['usd'],
            'l24_usd': data['market_data']['low_24h']['usd'],
            'market_cap_usd': data['market_data']['market_cap']['usd'],
            'public_interest_score': data['public_interest_score'],
            'liquidity_score': data['liquidity_score'],
        }
        for k in flow:
            # 2 days, when only twenty-four hours needed
            await self.cache.set_cache(k, 60 * 60 * 24 * 2, flow[k])
    