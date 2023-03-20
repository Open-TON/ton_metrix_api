"""Transatcions related."""
# Transactions are many to one for address
from fastapi import APIRouter

transactions_router = APIRouter()


@transactions_router.get('/daily/amount')
def tx_daily_avg_value():
    """Value in TON per tx for period."""
    #  gets all but first and last dates
    pass


@transactions_router.get('/daily/count')
def tx_daily_avg_count():
    """Transactions number/period."""
    # Fresh only(for written down)? Or for concrete period
    pass
