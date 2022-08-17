class DataStorage:
    '''
    Here we store all the tables in a dict:
        tables = {
            'title': Table()
        }
    '''

    def __init__(self):
        __slots__ = ('tables')
        self.tables = {}

    def add_table(self, table):
        self.tables[table.title] = table

    def get_table(self, title):
        return self.tables[title]

    def get_tables_titles(self):
        return self.tables.keys()
