import json
import discord

from ..base import CommandsGroup, commands
from ..utils import impersonate_message


class GeneralCommands(CommandsGroup):
    def __init__(self):
        self.pairs = dict()
        super().__init__()

    def export(self):
        return [self.savethis, self.process_request, self.emergency]

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
        self.pairs[alias] = url

    @commands('_')
    async def process_request(self, message: discord.Message):
        alias = message.content.split()[0][1:]
        url = self.pairs.get(alias, None)
        if url:
            await impersonate_message(message, url)

    @commands('emergency')
    async def emergency(self, message: discord.Message):
        await message.channel.send(json.dumps(self.pairs))
