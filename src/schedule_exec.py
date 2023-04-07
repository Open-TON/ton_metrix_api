import asyncio

from arq import create_pool, cron, Worker
from arq.connections import RedisSettings

from services.coingecko_consumer import GeckoClient


async def run_gecko(ctx):
    print('runs!')
    # g_c = GeckoClient()
    # await g_c.query_coin()

async def enq_init(ctx):
    print('init')


# worker = Worker(cron_jobs=[cron(run_gecko, second=set(range(0, 60, 3))),])
class WorkerSettings:

    # functions = [enq_init]

    cron_jobs = [
        cron(run_gecko, second=set(range(0, 60, 3))),
    ]

# async def main ():
#     redis = await create_pool(RedisSettings())
#     await redis.enqueue_job('enq_init')

# if __name__ == '__main__':
#     asyncio.run(main())
# worker.run_cron()
# print('stated')


# loop = asyncio.new_event_loop()
# loop.run_forever()
