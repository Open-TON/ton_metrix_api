"""Account information."""
from fastapi import APIRouter

accounts_router = APIRouter()


@accounts_router.get('/tx_sent/{address}')
def get_tx_sent_by_one(address: str):
    """Outgoing txs."""
    #  1. look in bd
    #  2. query http (or adnl)
    ...


# with cache!
@accounts_router.get('/balance/avg')
def get_account_avg_balance():
    """Balance over all known."""
    return {'avg_balance': 0}


@accounts_router.get('/tx_received/{address}')
def get_tx_received_by_one(address: str):
    """All txs received by concrete address."""
    ...


@accounts_router.get('/balance/over/{amount}')
def get_over_level(amount: int):
    """Greater accounts, percentage and number."""
    ...
