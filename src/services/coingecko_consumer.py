"""Big analytics player API client."""
import datetime as dt
from enum import Enum

from aiohttp import ClientSession


class GeckoCoinIDs(Enum):
    """Coingecko coin IDs from and for their API."""

    TON = 'the-open-network'
    ETH = 'ethereum'
    BTC = 'bitcoin'
    USD = 'usd'


GECKO_API = 'https://api.coingecko.com'


async def query_coin():
    """
    Financial data.

    The most part. Runs once in a day.
    """
    async with ClientSession(GECKO_API) as aio_cli:
        async with aio_cli.get(f'/api/v3/coins/{GeckoCoinIDs.TON.value}?tickers=false&'
                               f'developer_data=false&sparkline=false') as resp:
            data = await resp.json()
    flow = {
        'price_usd': data['market_data']['current_price']['usd'],
        'h24_usd': data['market_data']['high_24h']['usd'],
        'l24_usd': data['market_data']['low_24h']['usd'],
        'market_cap_usd': data['market_data']['market_cap']['usd'],
        'public_interest_score': data['public_interest_score'],
        'liquidity_score': data['liquidity_score'],
    }
    return flow


class CorrelationReceiver:
    """Gets currencies from Gecko API."""

    RELATIVE_CURRENCY = GeckoCoinIDs.USD.value
    MAIN_CURRENCY = GeckoCoinIDs.TON.value

    @staticmethod
    def clean_prices_sample(prices: list[list[int, float]]) -> list[float]:
        """Prices only from json as additional info doesn't needed."""
        return [p[1] for p in prices]

    @staticmethod
    def timestamps_corridor(hours_ago: int) -> tuple[float, float]:
        """Timestamps calculus."""
        dt_now = dt.datetime.now()
        ts_now = dt.datetime.timestamp(dt_now)
        ago_ts = dt.datetime.timestamp(dt_now - dt.timedelta(
            hours=hours_ago))
        return ago_ts, ts_now

    def make_request_url(self, token_id, hours_ago):
        """Parameters substitution."""
        ago_ts, ts_now = self.timestamps_corridor(hours_ago)
        return f'''coins/{token_id}/market_chart/range?
        vs_currency={self.RELATIVE_CURRENCY}&from={ago_ts}
        &to={ts_now}'''

    async def get_price_for_preiod(
            self, token_id: str, period_hours: int
    ) -> list[float]:
        """Query for a list of values for correlation processing."""
        # https://www.coingecko.com/en/api/documentation
        async with ClientSession(GECKO_API) as ses:
            async with ses.get(self.make_request_url(
                    token_id, period_hours)) as resp:
                res_json = await resp.json()
        return self.clean_prices_sample(res_json['price'])


class CorrelationCalculator:
    """Mathematics application over sample."""

    def __init__(self, provider: CorrelationReceiver):
        """Extract the data."""
        self.provider = provider

    @staticmethod
    def average(price_list: list) -> float:
        """Average as the part of calculus."""
        if not price_list:
            return 0
        return sum(price_list) / len(price_list)

    async def get_correlation_hours(
            self, currency: str, hours_ago: int
    ) -> float:
        """Linear correlation to data retrieved."""
        # https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%BE%D1%8D%D1%84%D1%84%D0%B8%D1%86%D0%B8%D0%B5%D0%BD%D1%82_%D0%BA%D0%BE%D1%80%D1%80%D0%B5%D0%BB%D1%8F%D1%86%D0%B8%D0%B8_%D0%9F%D0%B8%D1%80%D1%81%D0%BE%D0%BD%D0%B0&redirect=no
        ton = await self.provider.get_price_for_preiod(
            self.provider.MAIN_CURRENCY, hours_ago)
        currency = await self.provider.get_price_for_preiod(
            currency, hours_ago)
        avg_ton = self.average(ton)
        avg_cur = self.average(currency)
        numerator = denom_x = denom_y = 0
        for i, n in enumerate(ton):
            numerator += (avg_ton - n) * (
                avg_cur - currency[i]
            )
            denom_x += pow((avg_ton - n), 2)
            denom_y += pow((avg_cur - currency[i]), 2)
        denominator = pow(denom_x * denom_y, 0.5)
        if denominator == 0:
            return 1.0
        return numerator / denominator
