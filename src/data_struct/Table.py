class Table:
    '''
    Here we store all the table's data:
        title       -- a table's title
        columns     -- names of columns
        dtypes      -- types of data for each column
        keys        -- primary and foreign keys' names
        entries     -- all entries' data
    '''

    def __init__(self, title):
        __slots__ = ('title', 'columns', 'dtypes', 'keys', 'entries')
        self.title = title
        self.columns = []
        self.dtypes = []
        self.keys = {
            'primary_key': '',
            'foreign_keys': []
        }
        self.entries = {} # {entry_idx: {header: value}}


    def __repr__(self):
        return f'Title: {self.title}\n' + \
               f'{"-" * 30}\n\n' + \
               f'Columns ({len(self.columns)}): {self.columns}\n\n' + \
               f'Data types: {self.dtypes}\n\n' + \
               f'Keys: {self.keys}\n\n' + \
               f'Entries ({len(self.entries.keys())}): {self.entries}\n' + \
               f'{"=" * 30}'


    # Transform Table to dict.
    # WITHOUT `dtypes` and `keys`, because it is just parsed data
    def parsed_to_dict(self):
        table_to_dict = {
            'title': self.title,
            'columns': self.columns,
            'entries': self.entries
        }
        
        return table_to_dict
