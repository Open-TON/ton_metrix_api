from arq.connections import RedisSettings

from src.config import main_config
from src.services.tonapi import TonAPIClient


async def load_block(ctx, block_id):
    api = TonAPIClient()
    txs_data = api.tx_by_block(block_id)
    # todo: save data to the DB


async def main():
    pass


async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(main_config().cache.redis_url)
    functions = [load_block]

    on_startup = startup
    on_shutdown = shutdown
