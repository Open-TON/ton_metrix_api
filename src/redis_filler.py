import asyncio
import logging

from arq import create_pool
from arq.connections import RedisSettings

from schedule_exec import (
    ton_market_data, ton_volume,
    startup, on_job_start, on_job_end, CORREL_CURRENCIES_PACKS,
)

INIT_QUEUE = 'redis_init'
REQUEST_TIME_QUOTA = 60 / 10  # 10 - 30 rps, worst case
MINUTE_SECONDS = 60


class InitializationSettings:
    queue_name = INIT_QUEUE

    functions = [
        ton_market_data,
        ton_volume,
    ]
    on_startup = startup
    on_job_start = on_job_start
    on_job_end = on_job_end


async def init_cache():
    redis = await create_pool(RedisSettings())
    functions = [ton_volume, ton_market_data]
    init_delay = 0
    for f in functions:
        await redis.enqueue_job(
            f.__name__,
            _defer_by=init_delay,
            _queue_name=INIT_QUEUE,
        )
        init_delay += REQUEST_TIME_QUOTA
    for currency_funs in CORREL_CURRENCIES_PACKS:
        for k in currency_funs:
            await redis.enqueue_job(
                currency_funs[k].__name__,
                _defer_by=init_delay,
                _queue_name=INIT_QUEUE,
            )
            init_delay += REQUEST_TIME_QUOTA
    # need minute for timeout renewal
    logging.critical(
        'Wait %s seconds after this message '
        'before running main worker', init_delay + MINUTE_SECONDS)


if __name__ == '__main__':
    asyncio.run(init_cache())
