"""Pure financial data, TON."""
from fastapi import APIRouter
from fastapi import Depends
from starlette import status
from starlette.responses import JSONResponse

from databases.redis import redis_pool_acquer
from databases.redis import RedisRepo

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
        return JSONResponse(0, status_code=status.HTTP_404_NOT_FOUND)


@fin_router.get('/market_dominance')
async def dominance():
    """Part of the global market."""
