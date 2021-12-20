from ..base import PostgresDatabase


class LinkDatabase(PostgresDatabase):
    def __init__(self, DATABASE_URL):
        super().__init__(DATABASE_URL)

    def create_link_table(self):
        '''
        Create the table for links
        '''
        SQL = ("CREATE TABLE IF NOT EXISTS Links(",
               "id SERIAL PRIMARY KEY, name TEXT, ",
               "url TEXT)")
        return self.exec(SQL)
    
