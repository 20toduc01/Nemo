import discord
from matplotlib import pyplot as plt

from typing import Awaitable, Sequence


class CommandsGroup():
    def __init__(self) -> None:
        pass

    def export(self) -> Sequence[Awaitable]:
        raise NotImplementedError

    async def process(self, message: discord.Message) -> None:
        for command in self.export():
            await command(message)


def commands(trigger: str = None):
    def decorator(function: Awaitable) -> Awaitable:
        async def wrapper(instance, message: discord.Message):
            if (trigger is None 
                    or message.content.lower().startswith(trigger)): 
                await function(instance, message)
        return wrapper
    return decorator