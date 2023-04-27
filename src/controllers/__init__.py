"""Routers management."""
from fastapi import FastAPI

from src.controllers.accounts import accounts_router
from src.controllers.block import block_router
from src.controllers.exceptions import register_handle_errors
from src.controllers.fees import fees_router
from src.controllers.finance import fin_router
from src.controllers.social import social_networks_router
from src.controllers.transactions import transactions_router
from src.controllers.validators import validators_router


def init_controllers(app: FastAPI):
    """Routers initialization."""
    register_handle_errors(app)
    routers = [
        fin_router,
        accounts_router,
        fees_router,
        transactions_router,
        validators_router,
        block_router,
        social_networks_router,
    ]
    for router in routers:
        app.include_router(router)
