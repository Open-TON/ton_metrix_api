"""Block related metrics."""
from fastapi import APIRouter

block_router = APIRouter(prefix='/block')


@block_router.get('/height')
def block_height() -> int:
    """
    Last block seq num.

    :return integer
    """


@block_router.get('/interval/avg')
async def block_time(day: int) -> float:
    """
    Time spent to block for day **days ago**.

    :return float
    """


@block_router.get('/interval/median')
async def block_median_time(day: int) -> float:
    """
    Time median for a day.

    :return float
    """
