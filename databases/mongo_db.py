"""Mongo to business abstraction realization."""
# flake8: noqa
# todo rewrite to motor
from typing import Callable

from pymongo.command_cursor import CommandCursor
from pymongo.database import Database

####
# addresses contains balances
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


class NoMatch(Exception):
    pass


def field_extra_cursor(field_name):
    """Empty cursor handling"""
    def cursor_fetch_one(f: Callable):
        def except_empty(*args) -> int:
            cursor = f(*args)
            try:
                res = cursor.next()
            except StopIteration:
                return 0
            return res[field_name]
        return except_empty
    return cursor_fetch_one


class MongoRepo:
    """Mongo ops"""
    def __init__(self, db: Database):
        self._db = db
        self.addresses_col = self._db['addresses']
        self.txs_col = self._db['transactions']

    # todo apply `project` when tx will be in

    @field_extra_cursor('active_addresses')
    def get_active_addresses(self):
        return self.addresses_col.aggregate([
            {'$match': {'is_active': True}},
            {'$count': 'active_addresses'}
        ])

    @field_extra_cursor('average_all')
    def get_addresses_avg(self) -> CommandCursor:
        avg_all = self.addresses_col.aggregate([{
            '$group': {'_id': None, 'average_all': {'$avg': '$balance'}}
        }])
        return avg_all

    @field_extra_cursor('all_addresses_above')
    def get_addresses_over_watermark(self, balance: int):
        bigger_acs_count = self.addresses_col.aggregate([
            {'$match': {'balance': {'$gte':  balance}}},
            {'$count': 'all_addresses_above'}
        ])
        return bigger_acs_count

    @field_extra_cursor('zeros')
    def get_zero_balance(self) -> CommandCursor:
        # zero possibly can be just small values
        zeros_agg = self.addresses_col.aggregate([
            {'$match': {'balance': {'$eq': 0}}},
            {'$count': 'zeros'}
        ])
        return zeros_agg

    @field_extra_cursor('total_count')
    def total_entity(self, entity_name: str):
        if entity_name not in ['transactions', 'addresses']:
            raise NoMatch
        return self._db[entity_name].aggregate([
            {'$count': 'total_count'}
        ])
