# flake8: noqa
import pytest
from pymongo import MongoClient

from databases.mongo_db import MongoRepo
from databases.mongo_db import NoMatch


@pytest.fixture(scope='module')
def mongo_cli():
    m_c = MongoClient('mongodb://127.0.0.1')
    try:
        yield MongoRepo(m_c.addresses)
    finally:
        m_c.close()


@pytest.fixture(autouse=True, scope='module')
def test_data_mongo(mongo_cli):
    mongo_cli.addresses_col.drop()
    mongo_cli.txs_col.drop()
    result_txs = mongo_cli.txs_col.insert_many(
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
    mongo_cli.addresses_col.insert_many(
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
    mongo_cli.txs_col.drop()
    mongo_cli.addresses_col.drop()


def test_mongo_avgs(mongo_cli):
    assert mongo_cli.get_addresses_avg() == 117


def test_mongo_zeros(mongo_cli):
    assert mongo_cli.get_zero_balance() == 1


def test_mongo_above_watermark(mongo_cli):
    assert mongo_cli.get_addresses_over_watermark(-100) == 2
    assert mongo_cli.get_addresses_over_watermark(15) == 1
    assert mongo_cli.get_addresses_over_watermark(1_000) == 0


def test_amount_active(mongo_cli):
    assert mongo_cli.get_active_addresses() == 1


def test_total_amounts(mongo_cli):
    assert mongo_cli.total_entity('addresses') == 2
    assert mongo_cli.total_entity('transactions') == 2
    with pytest.raises(NoMatch):
        mongo_cli.total_entity('bridges')
