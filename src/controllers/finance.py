"""Pure financial data, TON."""
from fastapi import APIRouter
from fastapi import Depends
from starlette import status
from starlette.responses import JSONResponse

from databases.redis import redis_pool_acquer
from databases.redis import RedisRepo
from models.fins import CorrelationPeriod
from models.fins import CorrelationVs
from models.fins import PERIOD_TO_HOURS

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
        return JSONResponse(
            content={'message': 'Not up to date.'},
            status_code=status.HTTP_404_NOT_FOUND
        )


@fin_router.get('/market_dominance')
async def dominance():
    """Part of the global market."""


@fin_router.get('/correlation/{currency}/{period}')
async def correlation_value(
        period: CorrelationPeriod,
        currency: CorrelationVs, cache: RedisRepo = Depends(redis_pool_acquer)
):
    """Provide data on correlations."""
    period_to_hours = PERIOD_TO_HOURS[period.value]
    cor_val = await cache.check_cache(
        f'correlation_{currency.value}_{period_to_hours}')
    if cor_val:
        return cor_val
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Not up to date.'}
        )
