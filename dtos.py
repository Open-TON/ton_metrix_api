from enum import Enum

from pydantic import BaseModel


class TransactionType(Enum):
    ...


class Transactions(BaseModel):
    tx_hash: str
    tx_type: TransactionType
    fee: int
