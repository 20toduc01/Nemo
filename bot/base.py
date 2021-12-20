import discord
import psycopg2

from typing import Awaitable, Literal, Sequence


class CommandsGroup():
    def __init__(self) -> None:
        pass

    def export(self) -> Sequence[Awaitable]:
        raise NotImplementedError

    async def process(self, message: discord.Message) -> None:
        for command in self.export():
            await command(message)


class PostgresDatabase():
    def __init__(self, DATABASE_URL):
        self.db_url = DATABASE_URL
        self.conn = psycopg2.connect(self.db_url)

    def get_cursor(self):
        return self.conn.cursor()


    def exec(self, query):
        success = True
        cur = self.conn.cursor()
        try:
            cur.execute(query)
        except Exception as e:
            print(e)
            success = False
        cur.close()
        self.conn.commit()
        return success

    def fetch(self, query, mode: Literal['all', 'one'] = 'all'):
        success = True
        cur = self.conn.cursor()
        try:
            cur.execute(query)
        except Exception as e:
            print(e)
            success = False
        if success:
            if mode == 'all':
                result = cur.fetchall()
            else:
                result = cur.fetchone()
        else:
            result = None
        cur.close()
        self.conn.commit()
        return result


def commands(trigger: str = None):
    def decorator(function: Awaitable) -> Awaitable:
        async def wrapper(instance, message: discord.Message):
            if (trigger is None 
                    or message.content.lower().startswith(trigger)): 
                await function(instance, message)
        return wrapper
    return decorator