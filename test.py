import os

from dotenv import load_dotenv
from bot.emotes.emote_db import EmoteDatabase

load_dotenv()

db = EmoteDatabase(os.getenv('DATABASE_URL'))

# aa = db.exec(('CREATE TABLE Link (name TEXT, url TEXT, PRIMARY KEY (name))'))
# a = db.exec("INSERT INTO Link(name, url) VALUES ('test', 'test')")
print(db.exec("SELECT * FROM Link"))