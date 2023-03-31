"""Business models."""
from enum import Enum

from pydantic import BaseModel


class TransactionType(Enum):
    """Type of sides."""


class Transactions(BaseModel):
    """TX."""

    tx_hash: str
    tx_type: TransactionType
    fee: int
