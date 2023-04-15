"""Worker setup and task definition."""
from arq import cron
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from config import read_config
from databases.redis import RedisRepo
from models.fins import CacheMetricsUSD
from models.fins import GeckoCoinIDs
from services.coingecko_consumer import CorrelationCalculator
from services.coingecko_consumer import CorrelationReceiver
from services.coingecko_consumer import query_coin
from services.coingecko_consumer import query_volume
from services.coingecko_consumer import VolumeOps

RENEWAL_TIMEOUT_SEC = 180

HOUR_SECONDS = 60 * 60
WEEK_HOURS = 24 * 7
MONTH_HOURS = 24 * 30


async def startup(ctx):
    """Global jobs setup."""
    ctx['pool'] = ConnectionPool.from_url(read_config('/src/config.ini').cache.redis_url)


async def correlation(ctx, cur: str, hours: int):
    """From 3d party to Redis."""
    data_provider = CorrelationReceiver()
    correl_calc = CorrelationCalculator(data_provider)
    val = await correl_calc.get_correlation_hours(cur, hours)
    ttl_sec = hours * 60 * 60 + RENEWAL_TIMEOUT_SEC
    redis_writer = ctx['cache_writer']
    await redis_writer.set_expiring_cache(
        f'correlation_{cur}_{hours}', ttl_sec, val)


async def ton_market_data(ctx):
    """Cache market data."""
    market_data = await query_coin()
    cache_writer: RedisRepo = ctx['cache_writer']
    for k in market_data:
        await cache_writer.set_expiring_cache(k, HOUR_SECONDS, market_data[k])


async def ton_volume(ctx):
    """Volume change 24 - 24 ago."""
    volumes = await query_volume()
    vol_calculator = VolumeOps(volumes)
    cur_vol = vol_calculator.get_current_volume()
    vol_change = vol_calculator.get_volumes_percentage()
    cache_writer: RedisRepo = ctx['cache_writer']
    await cache_writer.set_expiring_cache(
        CacheMetricsUSD.CURRENT_VOLUME.value, HOUR_SECONDS, cur_vol)
    await cache_writer.set_expiring_cache(
        CacheMetricsUSD.VOLUME_CHANGE_24H_PERC.value,
        HOUR_SECONDS, vol_change)


async def on_job_end(ctx):
    """Close finished actions."""
    conn = ctx['cache_con']
    await conn.close(close_connection_pool=False)


async def on_job_start(ctx):
    """Jobs setup."""
    conn = Redis(connection_pool=ctx['pool'])
    redis_writer = RedisRepo(conn)
    ctx['cache_writer'] = redis_writer
    ctx['cache_con'] = conn


def currency_cor_hours(currency: str):
    """All periods for currency."""

    async def currency_1h(ctx):
        """Retrieve for 1 hour."""
        await correlation(ctx, currency, 1)

    async def currency_24h(ctx):
        """Calculate last day."""
        await correlation(ctx, currency, 24)

    async def currency_week(ctx):
        """Calculate current week."""
        await correlation(ctx, currency, WEEK_HOURS)

    async def cur_month(ctx):
        """Calculate current month."""
        await correlation(ctx, currency, MONTH_HOURS)

    return {
        'c_1h': currency_1h,
        'c_24h': currency_24h,
        'c_7d': currency_week,
        'c_30d': cur_month,
    }


ETH_CORRELATIONS = currency_cor_hours(GeckoCoinIDs.ETH.value)
BTC_CORRS = currency_cor_hours(GeckoCoinIDs.BTC.value)

CORREL_CURRENCIES_PACKS = [ETH_CORRELATIONS, BTC_CORRS]


class WorkerSettings:
    """Base worker setup."""

    on_startup = startup
    on_job_start = on_job_start
    on_job_end = on_job_end

    cron_jobs = []
    for c in CORREL_CURRENCIES_PACKS:
        cron_jobs.append(cron(c['c_1h'], minute=0, run_at_startup=True)),
        cron_jobs.append(cron(c['c_24h'], hour={0, 8, 16},
                              minute=3, run_at_startup=True)),
        cron_jobs.append(cron(c['c_7d'], weekday={1, 4}, hour=5,
                              minute=6, run_at_startup=True))
        cron_jobs.append(cron(c['c_30d'], day={1, 11, 21},
                              hour=5, minute=11, run_at_startup=True))
    cron_jobs.append(cron(ton_market_data, minute={1, 21, 41}))
    cron_jobs.append(cron(ton_volume, minute={2, 22, 42}))
