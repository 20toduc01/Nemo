import psycopg2
import requests

class EmoteDatabase():
    def __init__(self, DATABASE_URL):
        self.db_url = DATABASE_URL
        self.conn = psycopg2.connect(self.db_url)

    def get_conn(self):
        return self.conn

    def get_cursor(self):
        return self.conn.cursor()

    def find_emote_by_name(self, name, mode='startswith', fetch_all=False):
        '''
        Find an emote in the database by name

        Arguments:
            name (str) -- The name of the emote to find

        Returns:
            The emote if found, None otherwise
        '''
        SQL = f"SELECT * FROM Emotes WHERE name ILIKE '{'%' if mode == 'contains' else ''}{name}{'%' if mode != 'exact' else ''}'"
        cur = self.conn.cursor()
        cur.execute(SQL)
        result = cur.fetchall() if fetch_all else cur.fetchone()
        cur.close()
        return result

    def find_animated_emote_by_name(self, name, mode='startswith', fetch_all=False):
        '''
        Find an emote in the database by name

        Arguments:
            name (str) -- The name of the emote to find

        Returns:
            The emote if found, None otherwise
        '''
        SQL = f"SELECT * FROM AnimatedEmotes WHERE name ILIKE '{'%' if mode == 'contains' else ''}{name}{'%' if mode != 'exact' else ''}'"
        cur = self.conn.cursor()
        cur.execute(SQL)
        result = cur.fetchall() if fetch_all else cur.fetchone()
        cur.close()
        return result

    def add_emote(self, emote_name, emote_url):
        '''
        Add an emote with name emote_name and asset emote_url to the database

        Arguments:
            emote_name -- The name of the emote to add
            emote_url -- The asset url of the emote to add

        Returns:
            True if the emote was added, False otherwise
        '''
        # If an emote with the same name already exists, don't add it
        if self.find_emote_by_name(emote_name, mode='exact') is not None:
            return False

        # Proceed
        SQL = "INSERT INTO Emotes(name, image) VALUES (%s, %s)"
        image_bytes = requests.get(emote_url).content
        data = (emote_name, psycopg2.Binary(image_bytes))
        cur = self.conn.cursor()
        cur.execute(SQL, data)
        self.conn.commit()
        cur.execute('SELECT id FROM Emotes WHERE name ILIKE %s',
                    (emote_name, ))
        return cur.fetchone() != None

    def add_animated_emote(self, emote_name, emote_url):
        '''
        Add an animated emote with emote_name and asset emote_url to the database

        Arguments:
            emote_name -- The name of the emote to add
            emote_url -- The asset url of the emote to add

        Returns:
            True if the emote was added, False otherwise
        '''
        # If an emote with the same name already exists, don't add it
        if self.find_animated_emote_by_name(emote_name) is not None:
            return False

        # Proceed
        SQL = "INSERT INTO AnimatedEmotes(name, url) VALUES (%s, %s)"
        data = (emote_name, emote_url)
        cur = self.conn.cursor()
        cur.execute(SQL, data)
        self.conn.commit()
        return True

    def exec(self, query):
        cur = self.conn.cursor()
        try:
            a = cur.execute(query)
        except:
            return False
        finally:
            cur.close()
            self.conn.commit()
            return a
