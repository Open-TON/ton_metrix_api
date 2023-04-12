"""Correlation models."""
import enum


class CorrelationPeriod(enum.Enum):
    """Possible request params."""

    WEEK = '7d'
    HOUR = '1h'
    DAY = '1d'
    MONTH = '30d'
