"""Mongo to business abstraction realization."""
import datetime as dt
import random
import re
from functools import wraps
from typing import AsyncIterator, Callable

import pymongo
from fastapi import Depends
from motor.motor_asyncio import (AsyncIOMotorCollection,
                                 AsyncIOMotorCommandCursor,
                                 AsyncIOMotorDatabase)

from src.models.back_entities import DEVIATION_MAPPING, TelegramChat
from src.models.exceptions import EmptyCorridor
from src.utils import mongo_db

# flake8: noqa


####
# addresses contain balances
# addresses:
# - address - 0xabc
# - balance - int, nano or tons?
# - active (bool)
# - transactions(out and in) [objIds]
####
# transactions:
# - from
# - to
# - amount
# - fee
# - time
# - type
# - date
####
# telegram groups
# name?
# link
# language
# type
# number of users

async def mongo_service(m_db: AsyncIOMotorDatabase = Depends(mongo_db)):
    """Easy DI of async database service to controllers and other services."""
    yield MongoService(m_db)


class NoMatch(Exception):
    """No such entity found in the database."""
    pass


def field_extra_cursor(field_name):
    """Empty cursor handling."""

    def cursor_fetch_one(f: Callable):
        """Makes fn to return integer for sure."""

        @wraps(f)
        async def except_empty(*args) -> int:
            """As empty seqs raise."""
            cursor = f(*args)
            try:
                res = await cursor.next()
            except StopAsyncIteration:
                return 0
            return res[field_name]

        return except_empty

    return cursor_fetch_one


class MongoService:
    """Mongo cross abstraction."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self.addresses_col = self._db['addresses']
        self.channels = self._db['channels']
        self.txs_col = self._db['transactions']
        self.mock = self._db['network']
        self.prices = self._db['prices']

    # todo apply `project` when tx will be in
    async def add_chats(self, chats: list[TelegramChat]):
        """Chat savior."""
        data = [{'link': d.link,
                 'type': d.chat_type,
                 'language': d.language,
                 'population': []}
                for d in chats]
        await self.channels.insert_many(data)

    async def get_links(self, channel: bool) -> AsyncIterator[str]:
        """Chat links for worker."""
        if channel:
            async for ch in self.channels.find({'type': 'chan'}, {'link': 1}):
                yield ch['link']
        else:
            raise NotImplemented
        #     async for ch in self.channels.find({'type': {'$not': re.compile('')}},
        #                                        {'language': 1, 'link': 1}):
        #         yield ch['language'], ch['link']

    async def get_communities(self) -> AsyncIterator:
        """Inns members count provider."""
        async for ch in self.channels.find({
        'type': 'chan'}, {
            'link': 1, 'population': 1,
            '_id': 0
        }):
            yield ch

    async def save_timing_population(self, link: str, members: int):
        await self.channels.update_one(
            {'link': link}, {'$push': {'population': {
                'timestamp': int(dt.datetime.timestamp(dt.datetime.now())),
                'members': members
            }}})

    @field_extra_cursor('active_addresses')
    def get_active_addresses(self):
        """Addresses steel active."""
        return self.addresses_col.aggregate([
            {'$match': {'is_active': True}},
            {'$count': 'active_addresses'}
        ])

    @field_extra_cursor('average_all')
    def get_addresses_avg(self) -> AsyncIOMotorCommandCursor:
        """The total balance average."""
        avg_all = self.addresses_col.aggregate([{
            '$group': {'_id': None, 'average_all': {'$avg': '$balance'}}
        }])
        return avg_all

    @field_extra_cursor('all_addresses_above')
    def get_addresses_over_watermark(self, balance: int):
        """
        Divides the plenty of addresses and counts ones on top of slice.

        Example address A(100) is included in both: over 0 and over 10.
        """
        bigger_acs_count = self.addresses_col.aggregate([
            {'$match': {'balance': {'$gte': balance}}},
            {'$count': 'all_addresses_above'}
        ])
        return bigger_acs_count

    @field_extra_cursor('zeros')
    def get_zero_balance(self) -> AsyncIOMotorCommandCursor:
        """Getting count of empty accounts(SC, wallets e.t.c."""
        # zero possibly can be just small values
        zeros_agg = self.addresses_col.aggregate([
            {'$match': {'balance': {'$eq': 0}}},
            {'$count': 'zeros'}
        ])
        return zeros_agg

    @field_extra_cursor('total_count')
    def total_entity(self, entity_name: str):
        """Counts by entity."""
        if entity_name not in ['transactions', 'addresses']:
            raise NoMatch
        return self._db[entity_name].aggregate([
            {'$count': 'total_count'}
        ])

    async def get_series(
            self, start: int,
            end: int, step_seconds: int
    ) -> list[dict[str, int | float]]:
        """Provides timestamps with metrics list that lies in corridor."""
        records = [r async for r in self.mock.find(
            {'timestamp': {'$gte': start, '$lte': end}}).sort('timestamp')]
        if not records:
            raise EmptyCorridor
        # records.sort(key=lambda d: d['timestamp'], reverse=True)
        res = []
        timestamp = records[0]['timestamp']
        for r in records:
            if r['timestamp'] <= timestamp:
                res.append(r)
                timestamp += step_seconds - step_seconds * DEVIATION_MAPPING[step_seconds]
        return res

    async def get_series_v1(self, start: int,
            end: int, step_seconds: int
    ) -> list[dict[str, int | float]]:
        records = [r async for r in self.prices.find(
            {'timestamp': {'$gte': start, '$lte': end}}).sort('timestamp')]
        if not records:
            raise EmptyCorridor
        # records.sort(key=lambda d: d['timestamp'], reverse=True)
        res = []
        timestamp = records[0]['timestamp']
        # todo make corridor apply for 90% and 10% in second call
        for r in records:
            if r['timestamp'] >= timestamp:
                res.append(r)
                timestamp = r['timestamp']
                timestamp += step_seconds
        return res

    async def save_new_price(self, price: float, ts_now: int):
        """Insert one price, used in every 5 minutes."""
        await self.prices.insert_one({'timestamp': ts_now, 'price': price})

    async def apply_initial_prices(
            self, prices_preload: list[dict[int, float]]):
        await self.prices.insert_many(prices_preload)


class NetworkMock:
    """Fake network and price data maker."""
    FIVE_MINUTES_SECONDS = 300
    FINAL_ADDRESSES = 2_700_000
    FINAL_TXS = 50_000_000_000
    TIME_STEP = dt.timedelta(seconds=FIVE_MINUTES_SECONDS)
    ADDRESSES_STEP = lambda _: random.randrange(0, 7)
    TXS_STEP = lambda _: random.randrange(500, 200_000)
    PRICE = lambda _: random.randrange(200, 250) / 100
    PRICE_RULER = 50
    PRICE_STEP = lambda _: random.randrange(-10_000, 10_000) / 1_000_000

    def __init__(self, collection: AsyncIOMotorCollection):
        """Mocking database."""
        self.coll: AsyncIOMotorCollection = collection
        self._data: dict = {}

    def generate_addresses_transactions(self):
        """Generate data."""
        last_data_stamp = dt.datetime.timestamp(dt.datetime.now())
        start_dt = dt.datetime.timestamp(
            dt.datetime.now() - dt.timedelta(weeks=50))
        price_adjust = self.PRICE_RULER
        price = self.PRICE()
        for ts in range(int(last_data_stamp), int(start_dt), -self.FIVE_MINUTES_SECONDS):
            if price_adjust == 0:
                price = self.PRICE()
                price_adjust = self.PRICE_RULER
            self._data[ts] = {
                'addresses': self.FINAL_ADDRESSES,
                'transactions': self.FINAL_TXS,
                'price': price
            }
            price += self.PRICE_STEP()
            price_adjust -= 1
            self.FINAL_ADDRESSES -= self.ADDRESSES_STEP()
            self.FINAL_TXS -= self.TXS_STEP()

    async def write_down(self):
        """Save fake series."""
        series = []
        for k in self._data:
            series.append({'timestamp': k,
                           **self._data[k]})
        await self.coll.insert_many(series)
