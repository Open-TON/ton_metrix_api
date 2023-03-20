from fastapi import APIRouter
from starlette.requests import Request

accounts_router = APIRouter()


@accounts_router.get('/tx_sent/{address}')
def get_tx_sent_by_one(address: str):
    #  1. look in bd
    #  2. query http (or adnl)
    ...


# with cache!
@accounts_router.get('/balance/avg')
def get_account_avg_balance(request: Request):
    return {'avg_balance': 0}


@accounts_router.get('/tx_received/{address}')
def get_tx_received_by_one(address: str):
    ...


@accounts_router.get('/balance/over/{amount}')
def get_over_level(request: Request, amount: int):
    ...
