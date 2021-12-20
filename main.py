import os
import discord

from dotenv import load_dotenv

from bot.emotes.emote_cmd import EmoteCommands
from bot.general.general_cmd import GeneralCommands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
command_groups = []


@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    
    main_guild = client.get_guild(281418237156261889)
    
    emote_commands = EmoteCommands(os.getenv('DATABASE_URL'), main_guild)
    general_commands = GeneralCommands(os.getenv('DATABASE_URL'))

    global command_groups
    command_groups = [emote_commands, general_commands]

    # 816221905387782155 jm 281418237156261889 matngu


@client.event
async def on_message(message: discord.Message):
    for command_group in command_groups:
        await command_group.process(message)


client.run(TOKEN)
