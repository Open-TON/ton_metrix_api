"""Transactions related."""
# Transactions are many to two for address
from fastapi import APIRouter

transactions_router = APIRouter(prefix='/transactions')


@transactions_router.get('/daily/amount', tags=['for_period'])
async def tx_daily_avg_value(period_start: int, period_end: int) -> float:
    """Value in TON per tx for day."""
    #  gets all but first and last dates


@transactions_router.get('/daily/count', tags=['for_period'])
async def tx_daily_avg_count(period_start: int, period_end: int) -> float:
    """Transactions number/period."""
    # Max period by default?


@transactions_router.get('/last')
async def tx_time_avg() -> float:
    """
    Time over all types.

    :return: seconds for transaction
    """
    # Needs full txs history


@transactions_router.get('/by_type')
async def tx_by_type(tx_type: str) -> int:
    """
    Metrics on transaction types.

    :param tx_type: query param tx_type=nft or:
    bridge, defi, exchange
    :return: amount of transactions
    """
