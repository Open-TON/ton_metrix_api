"""Account information."""
import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status

from src.databases.mongo import mongo_service
from src.databases.mongo import MongoService
from src.models.dtos import DataResolutionSeconds
from src.models.dtos import NetBases
from src.models.dtos import NetBasesResponse
from src.models.exceptions import EmptyCorridor

accounts_router = APIRouter(prefix='/accounts')


@accounts_router.get('/network/data', response_model=NetBasesResponse)
async def network_base(
        start: int, end: int, resolution: DataResolutionSeconds,
        db_service: MongoService = Depends(mongo_service)
):
    """Mainnet accounts and transactions as activity indicator."""
    try:
        data = await db_service.get_series(
            start, end,
            resolution.value
        )
    except EmptyCorridor:
        logging.warning('No data for net bases %s - %s, %s',
                        start, end, resolution.value)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    res = []
    for d in data:
        res.append(NetBases(timestamp=d['timestamp'],
                            addresses_count=d['addresses'],
                            transactions_count=d['transactions']))
    return {'bases': res}


@accounts_router.get('/tx_sent/{address}')
async def tx_sent_by_one(address: str) -> int:
    """
    Outgoing txs.

    :param address - hex str
    :return int
    """
    #  1. look in bd
    #  2. query http (or adnl)
    ...


@accounts_router.get('/fresh')
async def recent_active_addresses() -> int:
    """
    Active for last day.

    :return integer, amount
    """


@accounts_router.get('/seen')
async def seen() -> int:
    """
    All addresses ever participated.

    :return all used accounts that can be retrieved in int
    """


# with cache!
@accounts_router.get('/balance/avg')
async def account_avg_balance() -> float:
    """
    Balance average over all known.

    :return float average from balances
    """
    ...


@accounts_router.get('/tx_received/{address}')
async def tx_received_by_one(address: str) -> int:
    """
    All txs received by concrete address.

    :param address hex str
    :return int number of txs
    """


@accounts_router.get('/balance/over')
async def over_level(tons: float) -> int:
    """
    Greater accounts, percentage and number.

    Also used in not zero check(ex. over 0 or 1 TON)

    :param tons balance in tons, float
    :return accounts with balance more than requested mark
    """


@accounts_router.get('/balance/quotas')
async def money_partitions() -> dict[int, float]:
    """
    Over level and percentage out of total.

    :return { level <int>: 'percentage of accouns over this one',
    ...}
    """
