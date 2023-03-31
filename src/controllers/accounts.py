"""Account information."""
from fastapi import APIRouter

accounts_router = APIRouter(prefix='/accounts')


@accounts_router.get('/tx_sent/{address}')
async def tx_sent_by_one(address: str) -> int:
    """Outgoing txs."""
    #  1. look in bd
    #  2. query http (or adnl)
    ...


@accounts_router.get('/fresh')
async def recent_active_addresses() -> int:
    """Active for last day."""


@accounts_router.get('/seen')
async def seen() -> int:
    """All addresses ever participated."""


# with cache!
@accounts_router.get('/balance/avg')
async def account_avg_balance() -> int:
    """Balance over all known."""
    ...


@accounts_router.get('/tx_received/{address}')
async def tx_received_by_one(address: str) -> int:
    """All txs received by concrete address."""


@accounts_router.get('/balance/over')
async def over_level(tons: int) -> int:
    """
    Greater accounts, percentage and number.

    Also used in not zero check(ex. over 0 or 1 TON)
    """


@accounts_router.get('/balance/quotas')
async def money_partitions() -> dict[int, float]:
    """Over level and percentage out of total."""
