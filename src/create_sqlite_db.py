import sqlite3
import os


def create_sqlite_db(sqlite_script_name):
    '''
    Create sqlite database using sqlite script.
    We save this database right in the top-level directory (`w3schools-sqlite-db`).
    '''

    # Create a database name from the script name
    db_file_name = sqlite_script_name.split('.')[0] + '.db'

    # If the database exists - remove it
    if os.path.exists(db_file_name):
        os.remove(db_file_name)

    print('-' * 30)
    print(f'Creating a {db_file_name} database... ', end='')

    # Create sqlite database and execute our script
    try:
        conn = sqlite3.connect(db_file_name)
        print(f'OK')
        cur = conn.cursor()

        with open(sqlite_script_name, 'r') as script_file:
            sql_script = script_file.read()

            try:
                cur.executescript(sql_script)
            except sqlite3.Warning as e:
                print('ERROR: ', end='')
                print(e)

        # Save the changes
        conn.commit()
        conn.close()

    except sqlite3.Warning as e:
        print('ERROR: ', end='')
        print(f'Database {db_file_name} not created.')
        print(e)
        