"""Business models."""
import enum
from enum import Enum

from pydantic import BaseModel


class FinBasic(BaseModel):
    """
    Toncoin actual financial data.

    Changes - for 24h.
    """

    price: float
    price_change_perc: float
    price_change: float
    market_cap: int
    market_cap_change_perc: float
    volume: int
    volume_change_perc_24h: float


class DataResolutionSeconds(enum.IntEnum):
    """Step in tickers choice."""

    HOUR = 60 * 60
    FIVE_MINUTES = 5 * 60
    DAILY = 24 * 60 * 60


class TransactionType(Enum):
    """Type of sides."""


class Transactions(BaseModel):
    """Wrap TXs."""

    tx_hash: str
    tx_type: TransactionType
    fee: int


class NetBases(BaseModel):
    """Mainnet actives."""

    timestamp: int
    addresses_count: int
    transactions_count: int


class NetBasesResponse(BaseModel):
    """Network visualization."""

    bases: list[NetBases]


class PriceTickerBlock(BaseModel):
    """Price minimal metrics."""

    timestamp: int
    price: float


class PriceResponse(BaseModel):
    """Parametrize price."""

    blocks: list[PriceTickerBlock]


class CommunityData(BaseModel):
    """TG community metrics."""

    link: str
    population: dict[int, int]


class CommunityResponse(BaseModel):
    """Telegram communities."""

    communities: list[CommunityData]
