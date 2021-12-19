import os
import discord

from dotenv import load_dotenv

from bot.emotes.emote_cmd import EmoteCommands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    
    main_guild = client.get_guild(281418237156261889)
    
    global emote_commands
    emote_commands = EmoteCommands(os.getenv('DATABASE_URL'), main_guild)
    # 816221905387782155 jm 281418237156261889 matngu


@client.event
async def on_message(message: discord.Message):
    await emote_commands.process(message)


client.run(TOKEN)
