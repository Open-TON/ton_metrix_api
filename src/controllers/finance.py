"""Pure financial data, TON."""
from fastapi import APIRouter

fin_router = APIRouter(prefix='/finance')


@fin_router.get('/market_cap')
async def capitalisation():
    """Market capitalisation."""


@fin_router.get('/market_dominance')
async def dominance():
    """Part of the global market."""
