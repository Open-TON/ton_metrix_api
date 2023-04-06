"""Big analytics player API client."""
from aiohttp import ClientSession

GECKO_TON_ID = 'the-open-network'


async def query_coin():
    """
    Financial data.

    The most part. Runs once in a day.
    """
    async with ClientSession('https://api.coingecko.com') as aio_cli:
        async with aio_cli.get(f'/api/v3/coins/{GECKO_TON_ID}?tickers=false&'
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
