import os
import time
import re
import random
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

from .data_struct.DataStorage import DataStorage
from .data_struct.Table import Table


PATH_TO_DRIVER = 'src/chromedriver'
os.environ['PATH'] = PATH_TO_DRIVER


def accept_cookies(driver):
    '''
    Processing the cookies dialog
    '''

    print('Waiting for a cookies dialog ... ', end='')
    try:
        # Wait for the dialog is loaded
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#accept-choices")))

        # Click 'accept'
        driver.find_element(By.CSS_SELECTOR, "#accept-choices").click() 
    except:
        print('No cookies')
    else:
        print('Cookies are accepted!')


def restore_DB(driver):
    '''
    Sometimes the list of tables' titles is not loaded, 
    so we need to restore a database by clicking on a "Restore Database" button
    '''

    print('Waiting for a database... ', end='')
    try:
        # Wait for the list of tables is loaded
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#yourDB > table > tbody > tr")))
    except:
        print('Restoring the database... ', end='')

        # Wait for the 'Restore Database' button is visible
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#restoreDBBtn")))
        
        # Click 'Restore Database'
        driver.find_element(By.CSS_SELECTOR, "#restoreDBBtn").click()

        # Click 'OK' on alert window
        Alert(driver).accept()

        print('Database is restored!')
    else:
        print('OK')
    finally:
        print('-' * 30)


def collect_data(driver):
    '''
    Parsing tables and collecting data
    '''

    print('Collecting tables\' data...')
    print()

    # Initialize a storage for all parsed tables
    data = DataStorage()

    # Waiting for the list of titles is loaded
    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#yourDB > table > tbody > tr")))

    # Get a number of tables by counting elements of the tables list
    n_tables = len(driver.find_elements(
        By.CSS_SELECTOR, "#yourDB > table > tbody > tr")[1:])

    # Go through the list of tables (i.e. for each table...)
    for tbl_idx in range(1, n_tables + 1):

        # Find table element in the list of tables
        tbl_element = driver.find_element(
            By.CSS_SELECTOR, f"#yourDB > table > tbody > tr:nth-child({tbl_idx + 1})")
        
        # Get the table's name
        table_title = tbl_element.text.split()[0]
        
        # Initialize and save a new table
        data.add_table(Table(table_title))

        # Load table data
        tbl_element.click()

        print(f'Collecting a table `{table_title}` ({tbl_idx}/{n_tables}){"...":<8}', end='')
        start_time = time.time()

        # Wait for the table with data is loaded
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#divResultSQL > div > table > tbody")))

        # Grab columns' names
        columns = []
        for col_element in driver.find_elements(
            By.CSS_SELECTOR, "#divResultSQL > div > table > tbody > tr:nth-child(1) > th"):
            columns.append(col_element.text)

        # Save columns' names to the storage
        data.get_table(table_title).columns = columns

        # Get number of entries
        n_entries = len(driver.find_elements(By.CSS_SELECTOR,
                        "#divResultSQL > div > table > tbody > tr")[1:])

        # Grab and save entries to the storage
        for entry_idx in range(1, n_entries + 1):
            data.get_table(table_title).entries[entry_idx] = {}
            for col, header in enumerate(data.get_table(table_title).columns, 1):
                data.get_table(table_title).entries[entry_idx][header] = driver.find_element(By.CSS_SELECTOR,
                                                                                           f"#divResultSQL > div > table > tbody > tr:nth-child({entry_idx + 1}) > td:nth-child({col})").text

        res_time = time.time() - start_time
        print(f'\tOK ({round(res_time, 3):<6} seconds, {n_entries:<3} entries)')


    return data


def determine_dtype(table):
    '''
    Here we (try to) determine types of data for each column
    '''

    dtypes = []

    # Regular expressions for some data types
    RE_INT = re.compile(r'(^\d{1,10}$)')
    RE_DOUBLE = re.compile(r'^(\d+\.\d*|\.?\d+)$')
    RE_DATE = re.compile(r'(^\d{4}[\/\-\.]([0-1]?[1-2])[\/\-\.](0[1-9]|1[1-9]?)$)' +
                         r'|(^(0[1-9]|1[1-9]?)[\/\-\.]([0-1]?[1-2])[\/\-\.]\d{4}$)')

    # For each column in the table...
    for col in table.columns:

        # Here we store all data of the current column. We will need it later
        all_data_from_col = []

        # We collect and save data of each entry of the current column
        for key in list(table.entries.keys()):
            cell_data = table.entries[key][col]
            all_data_from_col.append(cell_data)

        # Here we randomly choose some data for determine their data type later
        random_indexes = random.sample(range(len(all_data_from_col)), 
                                       min(10, len(all_data_from_col)))

        chosen_dtypes = []
        chosen_dtypes_counter = []

        # For each object of the randomly chosen from the current column 
        # we determine its data type and save it to the temporary list `chosen_dtypes`
        # and count the number of data types in the `chosen_dtypes_counter`.
        for idx in random_indexes:

            # Determine the data type
            if re.fullmatch(RE_INT, all_data_from_col[idx]):
                item_dtype = f'INTEGER'
            elif re.fullmatch(RE_DOUBLE, all_data_from_col[idx]):
                item_dtype = 'REAL'
            elif re.fullmatch(RE_DATE, all_data_from_col[idx]):
                item_dtype = 'NUMERIC'
            else:
                item_dtype = 'TEXT'

            # Save the data type
            if item_dtype not in chosen_dtypes:
                chosen_dtypes.append(item_dtype)
                chosen_dtypes_counter.append(0)

            # Increase counter
            chosen_dtypes_counter[chosen_dtypes.index(item_dtype)] += 1

        # Prioritize TEXT over other data types OR choose the most frequent
        if 'TEXT' in chosen_dtypes:
            col_dtype = 'TEXT'
        else:
            col_dtype = chosen_dtypes[chosen_dtypes_counter.index(
                max(chosen_dtypes_counter))]

        # Save final data type
        dtypes.append(col_dtype)


    return dtypes


def set_data_types(data):
    '''
    Determine data types for each table and save them to the storage
    '''

    # For each table...
    for title in data.tables.keys():
        dtypes = determine_dtype(data.get_table(title))
        data.get_table(title).dtypes = dtypes


def set_keys(data):
    '''
    Set primary and foreign keys for each table and save them to the storage
    '''

    primary_keys = []

    # Set primary key
    for title in data.tables.keys():
        data.get_table(title).keys['primary_key'] = data.get_table(
            title).columns[0]
        primary_keys.append(data.get_table(title).columns[0])

    # Set foreign keys
    for title in data.tables.keys():
        for header in data.get_table(title).columns[1:]:
            if header in primary_keys:
                data.get_table(title).keys['foreign_keys'].append(header)


def save_parsed_data_to_json(data, db_name):
    '''
    Save all parsed data to json-file.
    We save this json-file right in the top-level directory (`w3schools-sqlite-db`).
    '''

    json_file_name = db_name + '.json'
    data_to_dict = {}

    # Transform each table to dict and save to the dict structure
    for title, table in data.tables.items():
        data_to_dict[title] = table.parsed_to_dict()

    # Transform dict to json
    json_data = json.dumps(data_to_dict, indent=4)

    # Save all data to json-file
    with open(json_file_name, 'w+') as f:
        f.write(json_data)


def parse_data(url, db_name):
    '''
    Parsing tables from the w3schools test database
    '''

    # Setting webdriver options
    options = webdriver.ChromeOptions()
    options.service = PATH_TO_DRIVER  # path to the driver
    options.add_argument("--headless")  # without opening a browser window

    with webdriver.Chrome(options=options) as driver:
        print('Page loading... ', end='')
        try:
            driver.get(url)
        except:
            print('Too long waiting...')
        else:
            print('OK')

        accept_cookies(driver)

        restore_DB(driver)

        data = collect_data(driver)

        save_parsed_data_to_json(data, db_name)

        set_data_types(data)

        set_keys(data)

    return data
