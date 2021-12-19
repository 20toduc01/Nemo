import io
from typing import Callable, Sequence
import discord
from pprint import pformat

from ..base import CommandsGroup, commands
from ..utils import bytes_to_image, collate, impersonate_message
from .emote_db import EmoteDatabase
from .utils import emote_request, emotes_from_message, animated_emotes_from_message


class EmoteCommands(CommandsGroup):
    def __init__(self, database_connection_str: str, guild: discord.Guild):
        super().__init__()
        self.emote_db = EmoteDatabase(database_connection_str)
        self.active_map = dict()
        for emote in guild.emojis:
            data = self.emote_db.find_emote_by_name(emote.name.lower(), mode='exact')
            if data is None:
                self.emote_db.add_emote(
                    emote.name, f'https://cdn.discordapp.com/emojis/{emote.id}.png')
                self.active_map[emote.name.lower()] = 0
            else:
                self.active_map[emote.name.lower()] = data[3]

    def export(self):
        return [self.emoterank, self.delemote, self.changealias, 
                self.boostemote, self.addemote, self.addanimated,
                self.findemote, self.findanimated, self.process_request]

    @commands('emoterank')
    async def emoterank(self, message: discord.Message):
        await message.channel.send(pformat(self.active_map))

    @commands('delemote')
    async def delemote(self, message: discord.Message):
        result = self.emote_db.exec(
            f'DELETE FROM Emotes WHERE name ILIKE \'{message.content.split()[1]}\'')
        await message.channel.send('Done (maybe)')
    
    @commands('changealias')
    async def changealias(self, message: discord.Message):
        self.emote_db.exec(
            f'UPDATE Emotes SET name=\'{message.content.split()[2]}\' WHERE name ILIKE \'{message.content.split()[1]}\'')
        await message.channel.send('Done (maybe)')
        
    @commands('boostemote')
    async def boostemote(self, message: discord.Message):
        ename = message.content.split()[1]

        self.emote_db.exec(f"""UPDATE emotes SET use_count = 50 + (
                            SELECT use_count FROM emotes WHERE name ILIKE '{ename}'
                          )
                          WHERE name ILIKE '{ename}'""")
        if ename.lower() in self.active_map.keys():
            self.active_map[ename.lower()] = 50 + self.active_map[ename.lower()]
        await message.channel.send('Done (maybe)')

    @commands('addemote')
    async def addemote(self, message: discord.Message):
        result = self.emote_db.add_emote(message.content.split()[
                                    1], str(message.attachments[0].url))
        await message.channel.send('Successful' if result else 'Some error ocurred')

    @commands('addanimated')
    async def addanimated(self, message: discord.Message):
        emotename = message.content.split()[1]
        if len(message.content.split()) > 2:
            emoteurl = message.content.split()[2]
        else:
            emoteurl = str(message.attachments[0].url)
        print(emotename, emoteurl)
        self.emote_db.exec(
            f"""INSERT INTO AnimatedEmotes(name, url) VALUES ('{emotename}', '{emoteurl}')""")
    
    @commands('findanimated')
    async def findanimated(self, message: discord.Message):
        query = message.content.split()[1]
        cur = self.emote_db.get_cursor()
        cur.execute(
            f'SELECT * FROM AnimatedEmotes WHERE name ILIKE \'%{query}%\'')
        a = cur.fetchall()
        cur.close()
        await message.channel.send([x[1] for x in a])
    
    @commands('findemote')
    async def findemote(self, message: discord.Message):
        query = message.content.split()[-1]
        result = self.emote_db.find_emote_by_name(query, mode='contains', fetch_all=True)
        if result is not None:
            images = [bytes_to_image(x[2]) for x in result]
            names = [x[1] for x in result]
            fig = collate(images, cols=5, rows=5, titles=names)
            fig.savefig('./output/temp_grid.png')
            await message.channel.send(file=discord.File('./output/temp_grid.png'))
        else:
            await message.channel.send('No results')

    @commands()
    async def process_request(self, message: discord.Message):
        '''Update relevance score of emotes function and copy new emotes'''
        # Extract emotes names from message
        e_name, e_id = emotes_from_message(message)
        # Update relevance score of emotes
        for i in range(len(e_id)):
            if self.emote_db.find_emote_by_name(e_name[i]) is None:
                if self.emote_db.add_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.png'):
                    await message.channel.send(f'Added {e_name[i]} to database')
            self.emote_db.exec(
                f'UPDATE Emotes SET use_count = use_count + 1 WHERE name ILIKE \'{e_name[i]}\'')
            if e_name[i].lower() in self.active_map.keys():
                self.active_map[e_name[i].lower()] += 1

        '''Copy animated emotes'''
        e_name, e_id = animated_emotes_from_message(message)
        # Update relevance score of emotes
        for i in range(len(e_id)):
            if self.emote_db.find_animated_emote_by_name(e_name[i]) is None:
                if self.emote_db.add_animated_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.gif') is True:
                    await message.channel.send(f'Added {e_name[i]} to database')

        '''Process emote request'''
        request = emote_request(message)
        animated = self.emote_db.find_animated_emote_by_name(request)
        if animated is not None:
            await impersonate_message(message, animated[2] + '?size=64', 
                                      delete_original=True)
            return

        if request:
            # Find the emote in the database
            if message.content.endswith(':'):
                if request.lower() in self.active_map.keys():
                    return
                query = self.emote_db.find_emote_by_name(request, mode='exact')
            else:
                for active_emote in self.active_map.keys():
                    if request.lower() in active_emote:
                        return
                query = self.emote_db.find_emote_by_name(request, mode='startswith')
                if query is None:
                    query = self.emote_db.find_emote_by_name(request, mode='contains')
            # If the emote is found in the database
            if query:
                if message.guild.emoji_limit - len(self.active_map.keys()) <= 1:

                    least_used = 1e9
                    least_used_emote = None
                    for name, count in self.active_map.items():
                        if count < least_used:
                            least_used = count
                            least_used_emote = name
                    self.active_map.pop(least_used_emote)
                    # await message.channel.send(f'Deleting the least used emote that is {least_used_emote}')
                    for emote in message.guild.emojis:
                        if emote.name.lower() == least_used_emote:
                            await emote.delete()

                # Add the new emote to the active emote list
                new_emote = await message.channel.guild.create_custom_emoji(name=query[1], image=bytes(query[2]))
                # If it's successful
                if new_emote:
                    self.active_map[query[1].lower()] = query[3]
                    await impersonate_message(message, str(new_emote))
                    await message.delete()
            # If the emote is not found in the database
            else:
                pass
                # await message.channel.send('Not in the database. Use addemote command.')

        