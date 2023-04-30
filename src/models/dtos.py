"""Business models."""

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

