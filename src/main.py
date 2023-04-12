"""API entry point."""
import logging
from typing import Never

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio.connection import ConnectionPool

import logger
from config import read_config
from controllers import init_controllers
from docs import tags_metadata
from utils import mongo_db
from utils import redis_pool

logger.log()


def app() -> Never:
    """App runner."""
    app = FastAPI(
        debug=True,
        openapi_tags=tags_metadata
    )

    config_data = read_config('../config.ini')
    logging.info('Configuration file loaded...')

    redis_pooler = ConnectionPool.from_url(config_data.cache.redis_url)
    app.dependency_overrides[redis_pool] = lambda: redis_pooler
    mongo_client = AsyncIOMotorClient(config_data.db.dsn)
    app.dependency_overrides[mongo_db] = lambda: mongo_client[config_data.db.db_name]

    @app.on_event('shutdown')
    def shutdown_db_clients():
        """Gracefully shutdown connections to services."""
        mongo_client.close()
        redis_pooler.disconnect()
        logging.warning('Databases shutdown done.')

    init_controllers(app)
    return app


if __name__ == '__main__':
    app()
