from functools import wraps
import sqlite3
import os
import csv
import logging
from initial_db_setup_001 import create_database


def setup_logger():
    """
    Set up a logger configuration and return a logger instance.
    The logger is configured to write log messages to a file named 'my_log_file.log'. The log level is set to DEBUG,
    which includes all log messages. The log messages are formatted with the timestamp, log level, and the actual
    message content.
    Returns:
        logging.Logger: A logger instance that can be used to write log messages.
    """
    logging.basicConfig(
        filename='my_log_file.log',
        level=logging.DEBUG,  #
        format='%(asctime)s - %(levelname)s - %(message)s"'
    )
    return logging.getLogger('my_logger')


my_logger = setup_logger()


def db_connection_decorator(func):
    """
     A decorator that establishes a database connection, creates the database if it doesn't exist,
     executes the provided function with the connection, commits changes, and closes the connection.
     Args:
         func (function): The function to be wrapped.
     Returns:
         function: The wrapped function with added database connection handling.
     """

    @wraps(func)
    def wrap_the_function(*args, **kwargs):
        if not os.path.exists('my_data.db'):
            create_database(uniqueness='')
        conn = sqlite3.connect('my_data.db')
        result = func(conn, *args, **kwargs)
        conn.commit()
        conn.close()
        return result

    return wrap_the_function


@db_connection_decorator
def query_database(conn, query):
    """
    Execute a query on the database using the provided connection.
    Use for check data.
    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        query (str): The SQL query to execute.
    Returns:
        list: The list of fetched results from the database.
    Example:
         data = query_database('SELECT * FROM User')
    """
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


@db_connection_decorator
def add_user(conn, data1):
    """
    Add user or users to the database.
    Parameters:
    conn (sqlite3.Connection): The database connection.
    data1 (dict or list of dict): The user data to be added. Each dictionary should contain the following fields:
                                 - 'user_full_name': Full name of the user.
                                 - 'birth_day': Birth day of the user.
                                 - 'accounts': Accounts information of the user.
    """
    cursor = conn.cursor()

    if isinstance(data1, list):
        rows = [(row['user_full_name'].split()[0], row['user_full_name'].split()[1], row['birth_day'],
                 row['accounts']) for row in data1]
    else:
        rows = [(data1['user_full_name'].split()[0], data1['user_full_name'].split()[1], data1['birth_day'],
                 data1['accounts'])]

    cursor.executemany('INSERT INTO User (Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?)', rows)
    my_logger.info('Users added successfully')


@db_connection_decorator
def add_bank(conn, data1):
    """
       Add bank information to the database.
       Parameters:
           conn (sqlite3.Connection): The database connection.
           data1 (list or dict): Bank data(id and name) to be added.
       """
    cursor = conn.cursor()
    if isinstance(data1, list):
        rows = [(row['name'], row['id']) for row in data1]
    else:
        rows = [(data1['name'], data1['id'])]

    cursor.executemany('INSERT INTO Bank (Name, Id) VALUES (?, ?)', rows)
    my_logger.info('Banks added successfully')


@db_connection_decorator
def add_account(conn, data1):
    """
    Add account information to the database.
    Parameters:
        conn (sqlite3.Connection): The database connection.
        data1 (list or dict): Account data(user_id, type, account_number,bank_id, currency, amount, status) to be added.
    """
    cursor = conn.cursor()

    if isinstance(data1, list):
        rows = [(row['user_id'], row['type'], row['account_number'], row['bank_id'], row['currency'], row['amount'],
                 row['status']) for row in data1]
    else:
        rows = [(data1['user_id'], data1['type'], data1['account_number'], data1['bank_id'], data1['currency'],
                 data1['amount'], data1['status'])]

    cursor.executemany(
        'INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) VALUES '
        '(?, ?, ?, ?, ?, ?, ?)', rows)
    my_logger.info('Accounts added successfully')


@db_connection_decorator
def update_data_in_table(conn, table, user_id, new_name):
    """
    Update the name of a row in the specified table based on the provided user ID.
    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        table (str): The name of the table to update.
        user_id (int): The ID of the user whose name needs to be updated.
        new_name (str): The new name to set for the user.
    """
    cursor = conn.cursor()
    cursor.execute(f'UPDATE {table} SET Name = ? WHERE Id = ?', (new_name, user_id))
    conn.commit()
    my_logger.info(f'Name updated successfully in {table}')


def add_users_from_csv(path):
    """
    Add user data from a CSV file to the database.
    Args:
        path (str): The path to the CSV file containing user data.
    """
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        user_data = [{'user_full_name': row['Name'], 'birth_day': row['Birth_day'], 'accounts': row['Accounts']}
                     for row in reader]
        return add_user(user_data)


def add_banks_from_csv(path):
    """
    Add bank data from a CSV file to the database.
    Args:
        path (str): The path to the CSV file containing bank data.
    """
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        bank_data = [{'id': row['Id'], 'name': row['Bank']} for row in reader]
        return add_bank(bank_data)


def add_accounts_from_csv(path):
    """
    Add account data from a CSV file to the database.
    Args:
        path (str): The path to the CSV file containing account data.
    """
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        account_data = [{'user_id': row['User_id'], 'type': row['Type'], 'account_number': row['Account Number'],
                         'bank_id': row['Bank_id'], 'currency': row['Currency'], 'amount': row['Amount'],
                         'status': row['Status']} for row in reader]
        return add_account(account_data)


@db_connection_decorator
def modify_row(conn, table, user_id=None, bank_id=None, account_id=None, new_data=None):
    """
    Modify a row in the specified table based on the provided parameters.
    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        table (str): The name of the table to modify.
        user_id (int, optional): The ID of the user to modify (default: None).
        bank_id (int, optional): The ID of the bank to modify (default: None).
        account_id (int, optional): The ID of the account to modify (default: None).
        new_data (dict): A dictionary containing the new data to update.
    """
    cursor = conn.cursor()

    if table == 'User':
        cursor.execute(f'SELECT * FROM {table} WHERE Id = ?', (user_id,))
    elif table == 'Bank':
        cursor.execute(f'SELECT * FROM {table} WHERE Id = ?', (bank_id,))
    elif table == 'Account':
        cursor.execute(f'SELECT * FROM {table} WHERE Id = ?', (account_id,))
    else:
        my_logger.warning('Invalid table name')

    existing_row = cursor.fetchone()

    if not existing_row:
        my_logger.warning('Row not found')
        return

    query = f'UPDATE {table} SET'
    params = []

    for key, value in new_data.items():
        query += f' {key} = ?,'
        params.append(value)
    # query = ','.join([f' {key} = ?' for key in new_data.keys()])  #  smtg wrong
    # params = list(new_data.values())

    cursor.execute(query.rstrip(',') + f' WHERE Id = {existing_row[0]}', params)
    conn.commit()
    my_logger.info(f'Row in {table} modified successfully')


@db_connection_decorator
def delete_row(conn, table, row_id):
    """
       Delete a row from the specified table based on the provided row ID.
       Args:
           conn (sqlite3.Connection): The SQLite database connection.
           table (str): The name of the table to delete from.
           row_id (int): The ID of the row to delete.
       """
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM {table} WHERE Id = ?', (row_id,))
    existing_row = cursor.fetchone()

    if not existing_row:
        my_logger.warning(f'Row with Id {row_id} not found in {table}')
        return

    cursor.execute(f'DELETE FROM {table} WHERE Id = ?', (row_id,))

    my_logger.info(f'Row with Id {row_id} deleted from {table}')


users = [
    {'user_full_name': 'Johni O', 'birth_day': '1992-03-17', 'accounts': '12345'},
    {'user_full_name': 'Jane Babel', 'birth_day': '1984-07-10', 'accounts': '67890'}
]

banks_data = [
    {'name': 'Bank Ad', 'id': 31},
    {'name': 'Bank B', 'id': 73}
]

accounts_data = [
    {'user_id': 1, 'type': 'debit', 'account_number': '1501', 'bank_id': 1, 'currency': 'USD', 'amount': 5000,
     'status': 'silver'},
    {'user_id': 2, 'type': 'credit', 'account_number': '2471', 'bank_id': 2, 'currency': 'EUR', 'amount': 10000,
     'status': 'gold'}
]

add_user(users)
add_bank(banks_data)
add_account(accounts_data)

add_banks_from_csv('banks.csv')
add_accounts_from_csv('accounts.csv')
add_users_from_csv('users.csv')

modify_row(table='Account', account_id=7, new_data={'Amount': 8750})
modify_row('Bank', bank_id=57, new_data={'Name': 'New Bank Name', 'Id': 56})
delete_row('User', 6)
