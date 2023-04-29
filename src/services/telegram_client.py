import asyncio
import collections
import json
import logging

from pyrogram import Client
from pyrogram.types import Chat
from pyrogram.types import ChatPreview

from src.config import read_tg_client_conf
from src.models.back_entities import TelegramChat

API_REQUEST_TIMEOUT_SECONDS = 2


def client_factory() -> Client:
    config_data = read_tg_client_conf('config.ini')
    tg_client = Client(
        'group_counter',
        api_id=config_data.api_id,
        api_hash=config_data.api_hash
    )
    return tg_client


def get_national_chats() -> list[TelegramChat]:
    with open('services/ton_national_chats.json',
              encoding='utf8') as nat_chat_json:
        chats_json = json.load(nat_chat_json)['chats']
    chats_data: list[TelegramChat] = [
        TelegramChat(link=c['link'], language=c['language'], type=c['type']) for c in chats_json
    ]
    return chats_data


class UsersCounter:
    """Track groups population."""

    def __init__(self, client: Client, groups: dict[str, str]):
        """Counter and considered."""
        self.groups = groups
        self.client = client

    async def count_users(self, group_link: str) -> int:
        """Get main community members count."""
        async with self.client:
            try:
                chat_data = await self.client.get_chat(group_link)
            except Exception:
                logging.exception('Can`t join chat %s', group_link)
                raise
            if isinstance(chat_data, ChatPreview):
                await asyncio.sleep(API_REQUEST_TIMEOUT_SECONDS)
                await self.client.join_chat(group_link)
                chat_data: Chat = await self.client.get_chat(group_link)
        return chat_data.members_count

    async def num_languages(self) -> list[TelegramChat]:
        """Chat info producer."""
        chans_info = []
        for k in self.groups:
            try:
                count = await self.count_users(self.groups[k])
                chans_info.append(TelegramChat(link=self.groups[k], language=k, members=count))
            except Exception:
                logging.exception('Count fetch failed')
                continue
            finally:
                await asyncio.sleep(API_REQUEST_TIMEOUT_SECONDS)
        return chans_info

    async def users_partition(self, num_lang_communities: list[TelegramChat]) -> dict[str, float]:
        """Make national percentage of total count."""
        partition_percentage = collections.defaultdict(float)
        total_users = sum(ch.members for ch in num_lang_communities)
        if total_users == 0:
            raise ValueError
        for ch in num_lang_communities:
            partition_percentage[ch.language] += ch.members / total_users * 100
        return partition_percentage
