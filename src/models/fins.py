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


class CacheMetricsUSD(enum.Enum):
    """Aliasing metrics keys."""

    CURRENT_PRICE = 'current_price'
    PRICE_CHANGE_24H = 'price_change_24h'
    PRICE_CHANGE_24H_PERC = 'price_change_percentage_24h'
    CURRENT_MARKET_CAP = 'market_cap'
    MARKET_CAP_CHANGE_24H_PERC = 'market_cap_change_24h_percentage'
    CURRENT_VOLUME = 'current_volume'
    VOLUME_CHANGE_24H_PERC = 'volume_change_24h_perc'
    PRICE_HIGH_24H = 'price_high_24h'
    PRICE_LOW_24H = 'price_low_24h'
