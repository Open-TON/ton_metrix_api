"""Pure financial data, TON."""
from fastapi import APIRouter
from fastapi import Depends
from starlette import status
from starlette.responses import JSONResponse

from databases.redis import redis_pool_acquer
from databases.redis import RedisRepo
from src.models.fin_enums import CorrelationPeriod

fin_router = APIRouter(prefix='/finance')


@fin_router.get('/market_cap')
async def capitalisation(
        cache: RedisRepo = Depends(redis_pool_acquer)
):
    """Market capitalisation."""
    market_cap = await cache.check_cache('market_cap_usd')
    if market_cap:
        return market_cap
    else:
        return JSONResponse(content={'message': 'Not up to date.'},
                            status_code=status.HTTP_404_NOT_FOUND)


@fin_router.get('/market_dominance')
async def dominance():
    """Part of the global market."""


@fin_router.get('/correlation/{currency}/{period}')
async def correlation_value(
        period: CorrelationPeriod,
        currency, cache: RedisRepo = Depends(redis_pool_acquer)
):
    cor_val = await cache.check_cache()
    if cor_val:
        return cor_val
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={'message': 'Not up to date.'})
