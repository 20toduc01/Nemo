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


from functions import *
@client.event
async def on_message(message : discord.Message):
    global active_emotes, active_emotes_count, relevance_score, active_emotes_name, main_guild

    '''Check if user wants to explicitly add an emote to database'''
    if message.content.lower().startswith('addemote'):
        result = emote_db.add_emote(message.content.split()[-1], str(message.attachments[0].url))
        await message.channel.send('Successful' if result else 'Some error ocurred')


    '''Show all emotes by name'''
    if message.content.lower().startswith('findemote'):
        query = message.content.split()[-1]
        show_images(query, emote_db)
        await message.channel.send(file=discord.File('./output/temp_grid.png'))

    '''Copy new emotes to database'''


    '''Update relevance score of emotes function and copy new emotes'''
    # Extract emotes names from message
    e_name, e_id = emotes_from_message(message)
    # Update relevance score of emotes
    if len(e_id) > 0:
        for i in range(len(e_id)):
            found = False
            for j in range(len(active_emotes)):
                if active_emotes[j].id == e_id[i]:
                    relevance_score[j] += 0.1*(1 - np.log(relevance_score[j] + 1))
                    found = True
                    break
            if not found:
                # If not in the database
                if emote_db.find_emote_by_name(e_name[i]) is None:
                    if emote_db.add_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.png'):
                        await message.channel.send(f'Added {e_name[i]} to database')
        # Normalize relevance score
        relevance_score = relevance_score / (np.sum(relevance_score) + 1e-9)

    '''Copy animated emotes'''
    e_name, e_id = animated_emotes_from_message(message)
    # Update relevance score of emotes
    if len(e_id) > 0:
        for i in range(len(e_id)):
            if emote_db.find_animated_emote_by_name(e_name[i]) is None:
                if emote_db.add_animated_emote(e_name[i], f'https://cdn.discordapp.com/emojis/{e_id[i]}.gif') is True:
                    await message.channel.send(f'Added {e_name[i]} to database')
        # Normalize relevance score
        relevance_score = relevance_score / (np.sum(relevance_score) + 1e-9)


    '''Process emote request'''
    request = emote_request(message)
    animated = emote_db.find_animated_emote_by_name(request)
    if animated is not None:
        await impersonate_message(message, animated[2] + '?size=64')
        await message.delete()
        return

    if request:
        # If request is actually not valid
        for active_emote in active_emotes_name:
            if request.lower() in active_emote:
                return
        # Find the emote in the database
        query = emote_db.find_emote_by_name(request)
        # If the emote is found in the database
        if query:
            if message.guild.emoji_limit - len(active_emotes) <= 1:
                # Remove the least relevant emote from the active emote list
                min_index = np.argmin(relevance_score)
                relevance_score = np.delete(relevance_score, min_index)
                await active_emotes[min_index].delete()
                active_emotes.pop(min_index)

            # Add the new emote to the active emote list
            new_emote = await message.channel.guild.create_custom_emoji(name=query[1], image=bytes(query[2]))
            # If it's successful
            if new_emote:
                active_emotes.append(new_emote)
                active_emotes_name.append(new_emote.name.lower())
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