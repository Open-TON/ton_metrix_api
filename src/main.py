"""API entry point."""
import uvicorn
from fastapi import FastAPI

from src import logger
from src.controllers import init_controllers
from src.databases import database_un_load
from src.docs import tags_metadata


def app_factory() -> FastAPI:
    """App runner."""
    logger.log()

    app = FastAPI(
        debug=True,
        openapi_tags=tags_metadata
    )
    database_un_load(app)
    init_controllers(app)
    return app


if __name__ == '__main__':
    uvicorn.run(app_factory(), port=8087)
    # app_factory()
