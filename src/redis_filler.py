import asyncio

from arq import create_pool, worker
from arq.connections import RedisSettings

import datetime as dt

from schedule_exec import (
    ton_market_data, ton_volume,
    startup, on_job_start, on_job_end,
)


class InitializationSettings:
    functions = [
        ton_market_data,
        ton_volume,
    ]
    on_startup = startup
    on_job_start = on_job_start
    on_job_end = on_job_end


async def init_cache():
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job('ton_market_data',
                            _defer_by=dt.timedelta(
                                minutes=1))
    await redis.enqueue_job('ton_volume',
                            _defer_by=dt.timedelta(
                                minutes=1))

if __name__ == '__main__':
    asyncio.run(init_cache())
