"""Validator related controllers."""
from fastapi import APIRouter

validators_router = APIRouter(prefix='/validators')


@validators_router.get('/count')
async def all_validators_count() -> int:
    """No filters."""
    ...


@validators_router.get('/count/new')
async def get_new_validators(days_ago: int) -> int:
    """Appeared in period from day up to today."""
    ...


@validators_router.get('/count/potential', tags=['placeholder'])
async def potential_validators() -> int:
    """Not yet, no information on this."""


@validators_router.get('/count/activity')
async def get_validators_activity(active: bool) -> int:
    """
    Count by activity.

    :return validators count in int
    """


@validators_router.get('/stakes')
async def stakes_between_validators() -> dict[str, float]:
    """
    Stakes partition.

    :return: address to TONs stake
    """


@validators_router.get('/avg_reward')
async def average_reward_for(reward_for: str) -> float:
    """
    Rewards info.

    :param reward_for: 'stake' or 'validator'
    :return: TONS avg reward
    """
