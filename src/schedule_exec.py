from arq import cron, worker
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from services.coingecko_consumer import CorrelationReceiver, CorrelationCalculator, GeckoCoinIDs
from config import read_config
from databases.redis import RedisRepo


RENEWAL_TIMEOUT_SEC = 180


async def startup(ctx):
    ctx['pool'] = ConnectionPool.from_url(read_config('/home/ju_ry/PycharmProjects/ton_metr/ton_metrix_api/config.ini').cache.redis_url)


async def correlation(ctx, cur: str, hours: int):
    data_provider = CorrelationReceiver()
    correl_calc = CorrelationCalculator(data_provider)
    val = await correl_calc.get_correlation_hours(cur, hours)
    ttl_sec = hours * 60 * 60 + RENEWAL_TIMEOUT_SEC
    redis_writer = ctx['cache_writer']
    await redis_writer.set_expiring_cache(
        f'correlation_{cur}_{hours}', ttl_sec, val)


async def on_job_end(ctx):
    conn = ctx['cache_con']
    await conn.close(close_connection_pool=False)


async def on_job_start(ctx):
    conn = Redis(connection_pool=ctx['pool'])
    redis_writer = RedisRepo(conn)
    ctx['cache_writer'] = redis_writer
    ctx['cache_con'] = conn


def currency_cor_hours(currency: str):
    async def currency_1h(ctx):
        await correlation(ctx, currency, 1)
        
    async def currency_24h(ctx):
        await correlation(ctx, currency, 24)
        
    async def currency_week(ctx):
        await correlation(ctx, currency, 24 * 7)
        
    async def cur_month(ctx):
        await correlation(ctx, currency, 24 * 30)
        
    return {
        'c_1h': currency_1h,
        'c_24h': currency_24h,
        'c_7d': currency_week,
        'c_30d': cur_month,
    }


ETH_CORRELATIONS = currency_cor_hours(GeckoCoinIDs.ETH.value)
BTC_CORRS = currency_cor_hours(GeckoCoinIDs.BTC.value)

CORREL_CURRENCIES_PACKS = [ETH_CORRELATIONS, BTC_CORRS]

# worker = Worker(cron_jobs=[cron(run_gecko, second=set(range(0, 60, 3))),])
class WorkerSettings:
    
    on_startup  = startup
    on_job_start = on_job_start
    on_job_end = on_job_end

    cron_jobs = []
    for c in CORREL_CURRENCIES_PACKS:
        cron_jobs.append(cron(c['c_1h'], minute=0, run_at_startup=True)),
        cron_jobs.append(cron(c['c_24h'], hour={0, 8, 16},
                              minute=0, run_at_startup=True)),
        cron_jobs.append(cron(c['c_7d'], weekday={1, 4}, hour=5,
                              minute=0, run_at_startup=True))
        cron_jobs.append(cron(c['c_30d'], day={1, 11, 21},
                              hour=5, minute=11, run_at_startup=True))
# worker.run_worker(WorkerSettings)
