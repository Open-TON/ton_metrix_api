from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from starlette import status
from starlette.responses import JSONResponse

from src.databases.mongo import mongo_service
from src.databases.mongo import MongoService
from src.databases.redis import redis_pool_acquer
from src.databases.redis import RedisRepo
from src.models.dtos import CommunityResponse
from src.models.general import ZSET_KEY

social_networks_router = APIRouter(prefix='/social')


@social_networks_router.get(
    '/telegram/community',
    response_model=CommunityResponse
)
async def community_members(db_service: MongoService = Depends(mongo_service)):
    """Retrieve main telegram community groups stats."""
    communities = [c async for c in db_service.get_communities()]
    return {'communities': communities}


@social_networks_router.get('/telegram/national_ratios')
async def nationality_percentage_mapping(cache: RedisRepo = Depends(redis_pool_acquer)):
    """National chats size relationships."""
    ratios = await cache.get_zset(ZSET_KEY)
    if ratios:
        return JSONResponse(status_code=status.HTTP_200_OK, content=ratios)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No data.')
