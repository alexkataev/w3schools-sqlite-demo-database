def create_tables(data):
    '''
    Create a script for creating all tables
    '''

    # Final request/script
    req = ''

    # For each table...
    for table_name, table in data.tables.items():

        cur_req = f'''/*
 * Table structure for table `{table_name.lower()}`
 */
'''
        # Create table request
        cur_req += f'CREATE TABLE {table_name.lower()} (\n'

        # Add columns and primary key
        for i, col in enumerate(table.columns):
            if col == table.keys['primary_key']:
                cur_req += f'\t`{col}` {table.dtypes[i]} PRIMARY KEY AUTOINCREMENT,\n'
            else:
                cur_req += f'\t`{col}` {table.dtypes[i]} DEFAULT NULL,\n'
        
        # Add foreign keys
        for col in table.columns:
            if col in table.keys['foreign_keys']:
                for t_name, t in data.tables.items():
                    if t_name != table_name and col == t.keys['primary_key']:
                        foreign_key_ref_table = t_name.lower()
                        break
                cur_req += f'\tFOREIGN KEY({col}) REFERENCES {foreign_key_ref_table}({col}),\n'

        cur_req = cur_req[:-2] + '\n);\n\n'
        req += cur_req

    req += '/* -------------------------------------------------------- */\n\n'

    return req


def insert_into_tables(data):
    '''
    Insert data into tables
    '''

    # Final request/script
    req = ''
    
    # For each table...
    for table_name, table in data.tables.items():

        cur_req = f'''/*
 * Dumping data for table `{table_name.lower()}`
 */
'''
        cur_req += f'INSERT INTO {table_name.lower()} (`{("`, `").join(table.columns)}`) VALUES\n'
        
        for _, entry in table.entries.items():
            cur_req += f'{str(tuple(entry.values()))},\n'

        cur_req = cur_req[:-2] + ';\n\n'
        req += cur_req

    req += '/* -------------------------------------------------------- */\n\n'

    return req


def create_sqlite_script(data, sqlite_script_name):
    '''
    Create an sqlite script for creating an sqlite database later.
    We save this script right in the top-level directory (`w3schools-sqlite-db`).
    '''

    with open(sqlite_script_name, 'w+') as sqlite_script_file:

        sqlite_script_file.write('begin;\n\n')

        # Create and write script for the tables
        req = create_tables(data)
        sqlite_script_file.write(req)

        # Create and write script for the entries
        req = insert_into_tables(data)
        sqlite_script_file.write(req)

        sqlite_script_file.write('commit;')

