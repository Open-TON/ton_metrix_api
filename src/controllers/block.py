"""Block related metrics."""
from fastapi import APIRouter

block_router = APIRouter(prefix='/block')


@block_router.get('/height')
def block_height() -> int:
    """Last block seq num."""


@block_router.get('/interval/avg')
def block_time(day: int) -> float:
    """Time spent to block for day **days ago**."""


@block_router.get('/interval/median')
def block_median_time(day: int):
    """Time median for a day."""
