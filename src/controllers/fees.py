"""Fees related."""
from fastapi import APIRouter

fees_router = APIRouter(prefix='/fees')


@fees_router.get('/total', tags=['for_period'])
async def total_fees(period_start: int, period_end: int) -> float:
    """All fees taken over period."""


@fees_router.get('/avg')
async def avg_fees() -> float:
    """
    Fee per any transaction.

    :return fee over all txs ever done, float
    """
    # type? period?


@fees_router.get('/median', tags=['for_period'])
async def median_fee(period_start: int, period_end: int) -> float:
    """
    Period median without filters.

    :return float (as tons are too big)
    """
