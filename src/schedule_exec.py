"""Worker setup and task definition."""
import logging

from arq import cron
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from src.config import read_config
from src.databases.mongo import MongoService
from src.databases.redis import RedisRepo
from src.models.fins import CacheMetricsUSD
from src.models.fins import GeckoCoinIDs
from src.models.general import ZSET_KEY
from src.services.coingecko_consumer import CorrelationCalculator
from src.services.coingecko_consumer import CorrelationReceiver
from src.services.coingecko_consumer import query_coin
from src.services.coingecko_consumer import query_volume
from src.services.coingecko_consumer import VolumeOps
from src.services.telegram_client import client_factory
from src.services.telegram_client import UsersCounter

RENEWAL_TIMEOUT_SEC = 180

HOUR_SECONDS = 60 * 60
WEEK_HOURS = 24 * 7
MONTH_HOURS = 24 * 30
DAY_HOURS = 24


async def startup(ctx):
    """Global jobs setup."""
    config = read_config('config.ini')
    ctx['pool'] = ConnectionPool.from_url(config.cache.redis_url)
    ctx['mongo_db_srv'] = MongoService(AsyncIOMotorClient(config.db.dsn)[config.db.db_name])


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
    """Volume change 24h and 24h 24h ago."""
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

    currency_1h.__qualname__ = f'{currency_1h.__qualname__}_{currency}'
    currency_1h.__name__ = f'{currency_1h.__name__}_{currency}'

    async def currency_24h(ctx):
        """Calculate last day."""
        await correlation(ctx, currency, DAY_HOURS)

    currency_24h.__qualname__ = f'{currency_24h.__qualname__}_{currency}'
    currency_24h.__name__ = f'{currency_24h.__name__}_{currency}'

    async def currency_week(ctx):
        """Calculate current week."""
        await correlation(ctx, currency, WEEK_HOURS)

    currency_week.__qualname__ = f'{currency_24h.__qualname__}_{currency}'
    currency_week.__name__ = f'{currency_24h.__name__}_{currency}'

    async def cur_month(ctx):
        """Calculate current month."""
        await correlation(ctx, currency, MONTH_HOURS)

    cur_month.__qualname__ = f'{cur_month.__qualname__}_{currency}'
    cur_month.__name__ = f'{cur_month.__name__}_{currency}'

    return {
        'c_1h': currency_1h,
        'c_24h': currency_24h,
        'c_7d': currency_week,
        'c_30d': cur_month,
    }


ETH_CORRELATIONS = currency_cor_hours(GeckoCoinIDs.ETH.value)
BTC_CORRS = currency_cor_hours(GeckoCoinIDs.BTC.value)

CORREL_CURRENCIES_PACKS = [ETH_CORRELATIONS, BTC_CORRS]


async def get_chat_partition(ctx):
    mongo_srv: MongoService = ctx['mongo_db_srv']
    client = client_factory()
    groups = {lang: link async for lang, link in mongo_srv.get_links(main=False)}
    ucounter = UsersCounter(client, groups)
    cache: RedisRepo = ctx['cache_writer']
    async for ch in mongo_srv.get_links(main=True):
        community_count = await ucounter.count_users(ch)
        await mongo_srv.save_timing_population(ch, community_count)
    group_counts = await ucounter.num_languages()
    for tg_chat in group_counts:
        await mongo_srv.save_timing_population(tg_chat.link, tg_chat.members)
    try:
        partition = await ucounter.users_partition(group_counts)
    except ValueError:
        logging.error('Telegram users counter failed')
        return
    await cache.zset_add(ZSET_KEY, partition)


class WorkerSettings:
    """Base worker setup."""

    on_startup = startup
    on_job_start = on_job_start
    on_job_end = on_job_end
    #
    cron_jobs = []
    for c in CORREL_CURRENCIES_PACKS:
        cron_jobs.append(cron(c['c_1h'], minute=0)),
        cron_jobs.append(cron(c['c_24h'], hour={0, 8, 16},
                              minute=3)),
        cron_jobs.append(cron(c['c_7d'], weekday={1, 4}, hour=5,
                              minute=6))
        cron_jobs.append(cron(c['c_30d'], day={1, 11, 21},
                              hour=5, minute=11))
    cron_jobs.append(cron(ton_market_data, minute={1, 21, 41}))
    cron_jobs.append(cron(ton_volume, minute={2, 22, 42}))
    cron_jobs.append(cron(get_chat_partition, hour=2, minute=2, run_at_startup=True))
# worker.run_worker(WorkerSettings)
