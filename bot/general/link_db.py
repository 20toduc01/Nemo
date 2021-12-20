from ..base import PostgresDatabase


class LinkDatabase(PostgresDatabase):
    def __init__(self, DATABASE_URL):
        super().__init__(DATABASE_URL)

    def create_link_table(self):
        '''
        Create the table for links
        '''
        SQL = ("CREATE TABLE IF NOT EXISTS Links("
               "id SERIAL PRIMARY KEY, name TEXT, "
               "url TEXT)")
        return self.exec(SQL)
    
    def find_link_by_name(self, name, mode='startswith', fetch_all=False):
        '''
        Find an link in the database by name

        Arguments:
            name (str) -- The name of the emote to find

        Returns:
            The emote if found, None otherwise
        '''
        SQL = ("SELECT * FROM Links WHERE name ILIKE "
              f"'{'%' if mode == 'contains' else ''}{name}{'%' if mode != 'exact' else ''}'")
        result = self.fetch(SQL, mode='all' if fetch_all else 'one')
        return result
