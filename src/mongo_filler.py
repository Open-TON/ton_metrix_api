import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.databases.mongo import MongoService, NetworkMock
from src.services.coingecko_consumer import PriceLoader, convert_prices
from src.services.telegram_client import get_national_chats


async def main():
    aio_mongo = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    m_s = MongoService(aio_mongo['ton_storage'])
    await m_s.add_chats(get_national_chats())


async def net_bases():
    aio_mongo = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    generator = NetworkMock(aio_mongo['ton_storage']['network'])
    generator.generate_addresses_transactions()
    await generator.write_down()
    await generator.coll.create_index('timestamp')


async def real_prices():
    """Get all available data with built-in precision."""
    aio_mongo = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    m_s = MongoService(aio_mongo['ton_storage'])
    price_loader = PriceLoader()
    for price_res in await price_loader.get_whole_data():
        await m_s.apply_initial_prices(convert_prices(price_res))


if __name__ == '__main__':
    asyncio.run(real_prices())
