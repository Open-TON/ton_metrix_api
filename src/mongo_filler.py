import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from src.databases.mongo import MongoService
from src.databases.mongo import NetworkMock
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


if __name__ == '__main__':
    asyncio.run(net_bases())
