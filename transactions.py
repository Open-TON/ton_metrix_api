from fastapi import APIRouter
from starlette.requests import Request

transactions_router = APIRouter()


@transactions_router.get('/daily/amount')
def tx_daily_avg_value(request: Request):
    #  gets all but first and last dates
    pass


@transactions_router.get('/daily/count')
def tx_daily_avg_count(request: Request):
    pass

