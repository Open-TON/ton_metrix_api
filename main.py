"""API entry point."""
import logging
from typing import Never

import uvicorn
from fastapi import FastAPI
from pymongo import MongoClient
from redis.connection import ConnectionPool

import logger
from config import read_config
from controllers import init_controllers
from docs import tags_metadata
from utils import get_mongo_db
from utils import get_redis_pool

logger.log()


def app() -> Never:
    """App runner."""
    app = FastAPI(debug=True,
                  openapi_tags=tags_metadata
                  )

    config_data = read_config('config.ini')
    logging.info('Configuration file loaded...')

    redis_pool = ConnectionPool.from_url(config_data.cache.redis_url)
    app.dependency_overrides[get_redis_pool] = lambda: redis_pool
    mongo_client = MongoClient(config_data.db.dsn)
    app.dependency_overrides[get_mongo_db] = lambda: mongo_client[config_data.db.db_name]

    @app.on_event('shutdown')
    def shutdown_db_clients():
        """Gracefully shutdown connections to services."""
        mongo_client.close()
        redis_pool.disconnect()
        logging.warning('Databases shutdown done.')
    init_controllers(app)
    uvicorn.run(
        app
    )


if __name__ == '__main__':
    app()
