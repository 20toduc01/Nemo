import json
import discord

from bot.general.link_db import LinkDatabase

from ..base import CommandsGroup, commands
from ..utils import impersonate_message


class GeneralCommands(CommandsGroup):
    def __init__(self, database_connection_str: str):
        self.pairs_db = LinkDatabase(database_connection_str)
        super().__init__()

    def export(self):
        return [self.savethis, self.process_request]

    @commands('savethis')
    async def savethis(self, message: discord.Message):
        alias = message.content.split()[1]
        if message.attachments:
            url = message.attachments[0].url
        elif len(message.content.split()) > 2:
            url = message.content.split()[2]
        else:
            await message.channel.send('No url/content provided')
            return
        success = self.pairs_db.exec(f'INSERT INTO Links (name, url) VALUES (\'{alias}\', \'{url}\')')
        await message.channel.send('Done' if success else 'Failed')

    @commands('_')
    async def process_request(self, message: discord.Message):
        alias = message.content.split()[0][1:]
        query = self.pairs_db.find_link_by_name(alias, mode='exact')
        if query:
            await impersonate_message(message, query[2], delete_original=True)
