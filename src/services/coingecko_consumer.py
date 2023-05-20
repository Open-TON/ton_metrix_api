"""Big analytics player API client."""
import asyncio
import bisect
import datetime as dt
import logging

from aiohttp import ClientSession

from src.models.fins import CacheMetricsUSD, GeckoCoinIDs

GECKO_API = 'https://api.coingecko.com'


COINGECKO_API_TIMEOUT_SEC = 6


class BadRequest(Exception):
    """Request went 400."""


async def query_coin():
    """
    Financial data.

    The most part. Runs once in hour.
    """
    async with ClientSession(GECKO_API) as aio_cli:
        async with aio_cli.get(f'/api/v3/coins/{GeckoCoinIDs.TON.value}?tickers=false&'
                               f'developer_data=false&sparkline=false') as resp:
            data = await resp.json()
            try:
                market_data = data['market_data']
            except KeyError:
                logging.error('Error on basic retrieval, %s', resp.status)
                raise
    flow = {
        CacheMetricsUSD.CURRENT_PRICE.value:
            market_data['current_price']['usd'],
        CacheMetricsUSD.PRICE_HIGH_24H.value:
            market_data['high_24h']['usd'],
        CacheMetricsUSD.PRICE_CHANGE_24H_PERC.value:
            market_data['price_change_percentage_24h'],
        CacheMetricsUSD.PRICE_CHANGE_24H.value:
            market_data['price_change_24h'],
        CacheMetricsUSD.PRICE_LOW_24H.value:
            market_data['low_24h']['usd'],
        CacheMetricsUSD.CURRENT_MARKET_CAP.value:
            market_data['market_cap']['usd'],
        CacheMetricsUSD.MARKET_CAP_CHANGE_24H_PERC.value:
            market_data['market_cap_change_percentage_24h'],
    }
    return flow


async def query_volume():
    """Volume from individual endpoint for changes calculation."""
    async with ClientSession(GECKO_API) as ses:
        async with ses.get(f'/api/v3/coins/{GeckoCoinIDs.TON.value}/market_chart?'
                           f'vs_currency={GeckoCoinIDs.USD.value}&days=2') as resp:
            json_data = await resp.json()
    return json_data['total_volumes']


class VolumeOps:
    """Process volume data."""

    MS_IN_24H = 24 * 60 * 60 * 1000

    def __init__(self, volumes24: list[list[int | float]]):
        """Provide by query."""
        self.volumes24 = volumes24

    def get_current_volume(self) -> int:
        """Most timestamp value."""
        return self.volumes24[-1][1]

    def get_24_h_ago(self):
        """Get approximate timestamp."""
        return self.volumes24[-1][0] - self.MS_IN_24H

    def get_volume_24h_ago(self) -> int:
        """Find volume with the closest timestamp."""
        ts = self.get_24_h_ago()
        timestamps = [i[0] for i in self.volumes24]
        idx = bisect.bisect(timestamps, ts)
        if self.volumes24[idx][0] - ts > ts - self.volumes24[idx - 1][0]:
            return self.volumes24[idx - 1][1]
        return self.volumes24[idx][1]

    def get_volumes_percentage(self):
        """Compare to 24h ago, relatively to current."""
        cur_vol = self.get_current_volume()
        return (cur_vol - self.get_volume_24h_ago()) \
            / cur_vol * 100


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
        return (f'/api/v3/coins/{token_id}/market_chart/range?vs_currency='
                f'{self.RELATIVE_CURRENCY}&from={ago_ts}&to={ts_now}')

    # todo add rate limit on hit
    async def get_price_for_period(
            self, token_id: str, period_hours: int
    ) -> list[float]:
        """Query for a list of values for correlation processing."""
        # https://www.coingecko.com/en/api/documentation
        headers = {'content_type': 'application/json'}
        async with ClientSession(GECKO_API) as ses:
            async with ses.get(self.make_request_url(
                    token_id, period_hours),
                    headers=headers) as resp:
                res_json = await resp.json(
                    content_type=resp.content_type)
                if resp.status == 400:
                    logging.error('Bad request, %s', res_json)
                    raise BadRequest
        try:
            return self.clean_prices_sample(res_json['prices'])
        except KeyError:
            logging.error('Cannot get prices, %s', resp.status)
            raise


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
        ton = await self.provider.get_price_for_period(
            self.provider.MAIN_CURRENCY, hours_ago)
        currency = await self.provider.get_price_for_period(
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


class PriceLoader:
    """Operate with prices data from CoinGecko."""

    async def get_price_data(self, from_ts: float, to_ts: float):
        """Query resource provider."""
        async with ClientSession(GECKO_API) as ses:
            async with ses.get(f'/api/v3/coins/{GeckoCoinIDs.TON.value}'
                               '/market_chart/range?vs_currency=usd&'
                               f'from={int(from_ts)}&to={int(to_ts)}') as resp:
                json_data = await resp.json()
        return json_data['prices']

    async def get_whole_data(self):
        """Load database with ton price with various precision."""
        now = dt.datetime.now()
        now_tp = dt.datetime.timestamp(now)
        day_ago = now - dt.timedelta(
            days=1)
        season_ago = now - dt.timedelta(days=90)
        early_data = dt.datetime.timestamp(now - dt.timedelta(days=2_000))
        prec_5min = await self.get_price_data(dt.datetime.timestamp(
            day_ago + dt.timedelta(minutes=4)), now_tp)
        await asyncio.sleep(COINGECKO_API_TIMEOUT_SEC)
        prec_1hour = await self.get_price_data(
            dt.datetime.timestamp(season_ago + dt.timedelta(
                minutes=59)), dt.datetime.timestamp(day_ago))
        await asyncio.sleep(COINGECKO_API_TIMEOUT_SEC)
        prec_daily = await self.get_price_data(
            early_data, dt.datetime.timestamp(season_ago))
        return prec_5min, prec_1hour, prec_daily


def convert_prices(prices_data: list[list[int, float]]):
    return [{'timestamp': ts // 1000, 'price': price} for ts, price in prices_data]
