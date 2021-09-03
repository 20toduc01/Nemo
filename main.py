import os
from utils.general import *
from utils.emotes import *
import numpy as np
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

active_emotes = []
emote_db = EmoteDatabase(os.getenv('DATABASE_URL'))
main_guild = []

@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

    global active_emotes, active_emotes_count, relevance_score, active_emotes_name, main_guild
    global main_guild
    main_guild = client.get_guild(281418237156261889)
    # 816221905387782155 jm 281418237156261889 matngu
    active_emotes = get_server_emotes(main_guild)
    active_emotes_count = len(active_emotes)
    relevance_score = [1./len(active_emotes) for _ in range(len(active_emotes))]
    active_emotes_name = [emote.name.lower() for emote in active_emotes]


@client.event
async def on_message(message : discord.Message):
    global active_emotes, active_emotes_count, relevance_score, active_emotes_name, main_guild

    '''1. Check if user wants to add an emote to database'''
    if message.content.lower().startswith('addemote'):
        print(message.content.split()[-1], str(message.attachments[0].url))
        result = emote_db.addone(message.content.split()[-1], str(message.attachments[0].url))
        await message.channel.send('Successful' if result else 'Some error ocurred')

    '''1.5. Copy new emotes to database'''


    '''2. Update relevance score of emotes function and copy new emotes'''
    # Extract emotes names from message
    e_name, e_id = emotes_from_message(message)
    # Update relevance score of emotes
    if len(e_name) > 0:
        for i in range(len(e_name)):
            try:
                position = active_emotes_name.index(e_name[i].lower())
                print(e_name[i])
                relevance_score[position] += 0.1*(1 - np.log(relevance_score[position] + 1))
            except: # When the emote is not in the active emotes
                # If not in the database
                if emote_db.find_by_name(e_name[i]) is None:
                    if emote_db.addone(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.png') is not None:
                        await message.channel.send(f'Added {e_name[i]} to database')
        print(relevance_score)
        print('after')
        # Normalize relevance score
        relevance_score = relevance_score / (np.sum(relevance_score) + 1e-9)
        print(relevance_score)


    '''3. Process emote request'''
    request = emote_request(message)
    if request:
        # Find the emote in the database
        query = emote_db.find_by_name(request)
        # If the emote is found in the database
        if query:
            if message.guild.emoji_limit - len(active_emotes) <= 1:
                # Remove the least relevant emote from the active emote list
                min_index = np.argmin(relevance_score)
                relevance_score = np.delete(relevance_score, min_index)
                active_emotes_name.pop(min_index)
                await active_emotes[min_index].delete()
                active_emotes.pop(min_index)

            # Add the new emote to the active emote list
            new_emote = await add_emote(message.channel.guild, query[1], bytes(query[2]))
            # If it's successful
            if new_emote:
                active_emotes.append(new_emote)
                active_emotes_name.append(new_emote.name)
                relevance_score = np.append(relevance_score, 0.1)
                await impersonate_message(message, str(new_emote))
                await message.delete()
        # If the emote is not found in the database
        else:
            await message.channel.send('Not in the database. Use addemote command.')


    if message.content.startswith('test'):
        emotes = get_server_emotes(message.guild)
        await impersonate_message(message, "<:shitface:710909300087980123>")

        
client.run(TOKEN)