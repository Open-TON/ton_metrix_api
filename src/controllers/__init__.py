"""Routers management."""
from fastapi import FastAPI

from controllers.accounts import accounts_router
from controllers.block import block_router
from controllers.fees import fees_router
from controllers.transactions import transactions_router
from controllers.validators import validators_router


def init_controllers(app: FastAPI):
    """Routers initialization."""
    routers = [
        accounts_router,
        fees_router,
        transactions_router,
        validators_router,
        block_router
    ]
    for router in routers:
        app.include_router(router)
