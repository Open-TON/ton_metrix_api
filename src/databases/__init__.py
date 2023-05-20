"""Serving databases."""
import logging

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio.connection import ConnectionPool

from src.config import read_config
from src.utils import mongo_db
from src.utils import redis_pool


def database_un_load(app: FastAPI):
    """Database initialization with shutdown gracefully."""
    config_data = read_config(r'config.ini')
    logging.info('Configuration file loaded...')

    mongo_client = AsyncIOMotorClient(config_data.db.dsn)
    app.dependency_overrides[mongo_db] = lambda: mongo_client[config_data.db.db_name]
    redis_pooler = ConnectionPool.from_url(config_data.cache.redis_url)
    app.dependency_overrides[redis_pool] = lambda: redis_pooler

    @app.on_event('shutdown')
    async def shutdown_db_clients():
        """Gracefully shutdown connections to services."""
        mongo_client.close()
        await redis_pooler.disconnect()
        logging.warning('Databases shutdown done.')
