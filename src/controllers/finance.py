"""Pure financial data, TON."""
import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status

from src.databases.mongo import mongo_service
from src.databases.mongo import MongoService
from src.databases.redis import redis_pool_acquer
from src.databases.redis import RedisRepo
from src.models.dtos import DataResolutionSeconds
from src.models.dtos import FinBasic
from src.models.dtos import PriceResponse
from src.models.dtos import PriceTickerBlock
from src.models.exceptions import EmptyCorridor
from src.models.fins import CorrelationPeriod
from src.models.fins import CorrelationVs
from src.models.fins import PERIOD_TO_HOURS
from src.services.finance import finance_header

fin_router = APIRouter(prefix='/finance')


@fin_router.get('/market_cap')
async def capitalisation(
        cache: RedisRepo = Depends(redis_pool_acquer)
):
    """Market capitalisation."""
    market_cap = await cache.check_cache('market_cap_usd')
    if market_cap:
        return market_cap
    raise HTTPException(
        detail='Not up to date.',
        status_code=status.HTTP_404_NOT_FOUND,
    )


@fin_router.get('/market_dominance')
async def dominance():
    """Part of the global market."""


@fin_router.get('/ton/bases', response_model=FinBasic)
async def ton_data_daily(header_data=Depends(finance_header)):
    """Provide data and daily changes for the title."""
    if not all(header_data.values()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not up to date.'
        )
    return header_data


@fin_router.get('/correlation/{currency}/{period}')
async def correlation_value(
        period: CorrelationPeriod,
        currency: CorrelationVs,
        cache: RedisRepo = Depends(redis_pool_acquer)
):
    """Provide data on correlations."""
    period_to_hours = PERIOD_TO_HOURS[period.value]
    cor_val = await cache.check_cache(
        f'correlation_{currency.value}_{period_to_hours}')
    if cor_val:
        return cor_val
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not up to date.',
        )


@fin_router.get('/price', response_model=PriceResponse, tags=['for_period'])
async def price_ticker(
        start: int, end: int, resolution: DataResolutionSeconds,
        db_service: MongoService = Depends(mongo_service)
):
    """Customize price data."""
    try:
        data = await db_service.get_series(
            start, end,
            resolution.value
        )
    except EmptyCorridor:
        logging.warning('Data for prices missing, %s - %s, %s',
                        start, end, resolution.value)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {'blocks': [PriceTickerBlock(timestamp=d['timestamp'], price=d['price']) for d in data]}
