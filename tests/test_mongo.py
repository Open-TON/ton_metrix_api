"""Main database and its abstractions tests."""
# flake8: noqa
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.databases.mongo_db import MongoService
from src.databases.mongo_db import NoMatch


@pytest.fixture(scope='module')
def mongo_cli_fxt():
    """Filler fixture."""
    m_c = MongoClient('mongodb://127.0.0.1')
    try:
        yield MongoService(m_c['ton_storage'])
    finally:
        m_c.close()


@pytest.fixture(scope='module')
def mongo_cli():
    """Async client for tests."""
    aio_mongo = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    try:
        yield MongoService(aio_mongo['ton_storage'])
    finally:
        aio_mongo.close()


@pytest.fixture(autouse=True, scope='module')
def test_data_mongo(mongo_cli_fxt):
    """Prefilling and closing up on teardown."""
    mongo_cli_fxt.addresses_col.drop()
    mongo_cli_fxt.txs_col.drop()
    result_txs = mongo_cli_fxt.txs_col.insert_many(
        [
            {
                'from': 0x123443af2302, 'to': 0x123444af5302,
                'value': 45, 'dt': 1234567, 'fee': 1,
            },
            {
                'from': 0x123444af53020, 'to': 0x123443af2302,
                'value': 104, 'dt': 1234567, 'fee': 2,
            },
        ]
    )
    mongo_cli_fxt.addresses_col.insert_many(
        [
            {
                'address': 0x123443af2302, 'balance': 234,
                'is_active': True, 'txs': result_txs.inserted_ids,
            },
            {
                'address': 0x123444af5302, 'balance': 0,
                'is_active': False, 'txs': result_txs.inserted_ids,
            },
        ]
    )
    yield
    mongo_cli_fxt.txs_col.drop()
    mongo_cli_fxt.addresses_col.drop()


@pytest.mark.asyncio
async def test_mongo_avgs(mongo_cli):
    """(234 + 0) / 2."""
    assert await mongo_cli.get_addresses_avg() == 117


@pytest.mark.asyncio
async def test_mongo_zeros(mongo_cli):
    """1 provided."""
    assert await mongo_cli.get_zero_balance() == 1


@pytest.mark.asyncio
async def test_mongo_above_watermark(mongo_cli):
    """Watermark classification function test by fixtures."""
    assert await mongo_cli.get_addresses_over_watermark(-100) == 2
    assert await mongo_cli.get_addresses_over_watermark(15) == 1
    assert await mongo_cli.get_addresses_over_watermark(1_000) == 0


@pytest.mark.asyncio
async def test_amount_active(mongo_cli):
    """Activity parameter filtering."""
    assert await mongo_cli.get_active_addresses() == 1


@pytest.mark.asyncio
async def test_total_amounts(mongo_cli):
    """Entity counter functionality."""
    assert await mongo_cli.total_entity('addresses') == 2
    assert await mongo_cli.total_entity('transactions') == 2
    with pytest.raises(NoMatch):
        await mongo_cli.total_entity('bridges')
