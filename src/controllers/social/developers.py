from fastapi import APIRouter

dev_router = APIRouter(prefix='/dev')


@dev_router.get('/total')
async def dev_count():
    """Approximate developer count on GitHub."""
