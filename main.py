import os
from re import search
from utils.general import *
from utils.emotes import *
import numpy as np
import discord
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

emote_db = EmoteDatabase(os.getenv('DATABASE_URL'))
main_guild = None
active_map = dict()


@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    global main_guild, active_map
    main_guild = client.get_guild(281418237156261889)
    for emote in main_guild.emojis:
        data = emote_db.find_emote_by_name(emote.name.lower(), mode='exact')
        if data is None:
            emote_db.add_emote(emote.name, f'https://cdn.discordapp.com/emojis/{emote.id}.png')
            active_map[emote.name.lower()] = 0
        else:
            active_map[emote.name.lower()] = data[3]
    print(active_map)
    # 816221905387782155 jm 281418237156261889 matngu


from functions import *
@client.event
async def on_message(message : discord.Message):
    global main_guild

    if message.content.lower().startswith('emoterank'):
        await message.channel.send(active_map)

    '''Delete an emote function'''
    if message.content.lower().startswith('delemote'):
        result = emote_db.exec(f'DELETE FROM Emotes WHERE name ILIKE \'{message.content.split()[1]}\'')
        await message.channel.send('Done (maybe)')

    '''Change alias of an emote'''
    if message.content.lower().startswith('changealias'):
        emote_db.exec(f'UPDATE Emotes SET name=\'{message.content.split()[2]}\' WHERE name ILIKE \'{message.content.split()[1]}\'')
        await message.channel.send('Done (maybe)')

    #test

    '''Boost use count of an emote'''
    if message.content.lower().startswith('boostemote'):
        ename = message.content.split()[1]
        
        emote_db.exec(f"""UPDATE emotes SET use_count = 50 + (
                            SELECT use_count FROM emotes WHERE name ILIKE '{ename}'
                          )
                          WHERE name ILIKE '{ename}'""")
        if ename.lower() in active_map.keys():
            active_map[ename.lower()] = 50 + active_map[ename.lower()]
        await message.channel.send('Done (maybe)')

    '''Check if user wants to explicitly add an emote to database'''
    if message.content.lower().startswith('addemote'):
        result = emote_db.add_emote(message.content.split()[1], str(message.attachments[0].url))
        await message.channel.send('Successful' if result else 'Some error ocurred')

    if message.content.lower().startswith('addanimated'):
        emotename = message.content.split()[1]
        if len(message.content.split()) > 2:
            emoteurl = message.content.split()[2]
        else:
            emoteurl = str(message.attachments[0].url)
        print(emotename, emoteurl)
        emote_db.exec(f"""INSERT INTO AnimatedEmotes(name, url) VALUES ('{emotename}', '{emoteurl}')""")

    '''Find animated emotes'''
    if message.content.lower().startswith('findanimated'):
        query = message.content.split()[1]
        cur = emote_db.get_cursor()
        cur.execute(f'SELECT * FROM AnimatedEmotes WHERE name ILIKE \'%{query}%\'')
        a = cur.fetchall()
        cur.close()
        await message.channel.send([x[1] for x in a])


    '''Show all emotes by name'''
    if message.content.lower().startswith('findemote'):
        query = message.content.split()[-1]
        show_images(query, emote_db)
        await message.channel.send(file=discord.File('./output/temp_grid.png'))


    '''Update relevance score of emotes function and copy new emotes'''
    # Extract emotes names from message
    e_name, e_id = emotes_from_message(message)
    # Update relevance score of emotes
    for i in range(len(e_id)):
        if emote_db.find_emote_by_name(e_name[i]) is None:
            if emote_db.add_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.png'):
                await message.channel.send(f'Added {e_name[i]} to database')
        emote_db.exec(f'UPDATE Emotes SET use_count = use_count + 1 WHERE name ILIKE \'{e_name[i]}\'')
        if e_name[i].lower() in active_map.keys():
            active_map[e_name[i].lower()] += 1
    
    '''Copy animated emotes'''
    e_name, e_id = animated_emotes_from_message(message)
    # Update relevance score of emotes
    for i in range(len(e_id)):
        if emote_db.find_animated_emote_by_name(e_name[i]) is None:
            if emote_db.add_animated_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.gif') is True:
                await message.channel.send(f'Added {e_name[i]} to database')


    '''Process emote request'''
    request = emote_request(message)
    animated = emote_db.find_animated_emote_by_name(request)
    if animated is not None:
        await impersonate_message(message, animated[2] + '?size=64')
        await message.delete()
        return

    if request:
        # If request is actually not valid
        
        # Find the emote in the database
        if message.content.endswith(':'):
            if request.lower() in active_map.keys(): return
            query = emote_db.find_emote_by_name(request, mode='exact')
        else:
            for active_emote in active_map.keys():
                if request.lower() in active_emote:
                    return
            query = emote_db.find_emote_by_name(request, mode='startswith')
            if query is None:
                query = emote_db.find_emote_by_name(request, mode='contains')
        # If the emote is found in the database
        if query:
            if message.guild.emoji_limit - len(active_map.keys()) <= 1:
                
                least_used = 1e9
                least_used_emote = None
                for name, count in active_map.items():
                    if count < least_used:
                        least_used = count
                        least_used_emote = name
                active_map.pop(least_used_emote)
                # await message.channel.send(f'Deleting the least used emote that is {least_used_emote}')
                for emote in message.guild.emojis:
                    if emote.name.lower() == least_used_emote:
                        await emote.delete()

            # Add the new emote to the active emote list
            new_emote = await message.channel.guild.create_custom_emoji(name=query[1], image=bytes(query[2]))
            # If it's successful
            if new_emote:
                active_map[query[1].lower()] = query[3]
                await impersonate_message(message, str(new_emote))
                await message.delete()
        # If the emote is not found in the database
        else:
            pass
            # await message.channel.send('Not in the database. Use addemote command.')

        
client.run(TOKEN)