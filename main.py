from src.data_parser import parse_data
from src.create_sqlite_script import create_sqlite_script
from src.create_sqlite_db import create_sqlite_db

import time


if __name__ == "__main__":

    start_time = time.time()

    # Parse tables 
    url = "https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all"
    db_name = 'w3schools'
    data = parse_data(url, db_name)

    # Create sqlite script -- we use it for creating sqlite database.
    sqlite_script_name = db_name + '.sql'
    create_sqlite_script(data, sqlite_script_name)

    # Create sqlite database using sqlite script
    create_sqlite_db(sqlite_script_name)
    
    print('-' * 30)
    res_time = time.time() - start_time
    print(f'Total time: {res_time / 60:.2} mins')
    print('=' * 30)
    print('Complete!')
    print()
