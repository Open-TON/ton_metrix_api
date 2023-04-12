"""Correlation models."""
import enum


class CorrelationPeriod(enum.Enum):
    """Possible request params."""

    WEEK = '7d'
    HOUR = '1h'
    DAY = '1d'
    MONTH = '30d'


class GeckoCoinIDs(enum.Enum):
    """Coingecko coin IDs from and for their API."""

    TON = 'the-open-network'
    ETH = 'ethereum'
    BTC = 'bitcoin'
    USD = 'usd'


class CorrelationVs(enum.Enum):
    """Actives to correlate against."""

    BTC = 'btc'
    ETH = 'eth'
    GOLD = 'gold'


PERIOD_TO_HOURS = {
    '1h': 1,
    '1d': 24,
    '7d': 24 * 7,
    '30d': 24 * 30,
}
