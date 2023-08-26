import sqlite3
import csv
from logger import setup_logger
from db_decorator import db_connection_decorator
from validation import valid_full_name, validate_strict_account_fields, validate_account_number

my_logger = setup_logger()


def prepare_rows(input_data):
    """
    Prepare rows for insertion into the database using executemany.
    Parameters:
        input_data: Account or Bank data to be added. Each element should be a dictionary representing a record.

    Returns:
        list: A list of tuples, where each tuple represents a row to be inserted into the database.
    """
    data = input_data[0] if isinstance(input_data[0], list) else input_data
    return [tuple(row.values()) for row in data]


@db_connection_decorator
def add_user(cursor, input_data):
    """
        Add user information to the database.
        Parameters:
            cursor (sqlite3.Connection): The database connection.
            input_data: User data containing dictionaries with keys 'user_full_name', 'birth_day', and 'accounts'.
                Each dictionary represents a user to be added.
        Note:
            The 'user_full_name' is split into 'Name' and 'Surname' columns in the database.
        Returns:
            None
        """
    data = input_data[0] if isinstance(input_data[0], list) else input_data
    rows = [(row['id'], *valid_full_name(row['user_full_name']), row['birth_day'], row['accounts']) for row in data]
    cursor.executemany('INSERT INTO User (Id, Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?, ?)', rows)
    my_logger.info('Users added successfully')


@db_connection_decorator
def add_bank(cursor, *input_data):
    """
    Add bank information to the database.
    Parameters:
        cursor (sqlite3.Connection): The database connection.
        cursor (sqlite3.Connection): The database connection.
        input_data (list or dict): Bank data (id and name) to be added.
    """
    rows = prepare_rows(input_data)
    cursor.executemany('INSERT INTO Bank (Name, Id) VALUES (?, ?)', rows)
    my_logger.info('Banks added successfully')


@db_connection_decorator
def add_account(cursor, input_data):
    """
    Add account information to the database.
    Parameters:
        cursor (sqlite3.Connection): The database connection.
        input_data: Account data to be added. Each element should be a dictionary representing an account,
            containing keys 'User_id', 'Type', 'Account_Number', 'Bank_id', 'Currency', 'Amount', and 'Status'.
    Returns:
        None
    """

    validate_strict_account_fields(input_data)

    for i in input_data:
        validate_account_number(i['account_number'])

    rows = prepare_rows(input_data)
    cursor.executemany('INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) VALUES '
                       '(?, ?, ?, ?, ?, ?, ?)', rows)
    my_logger.info('Accounts added to database successfully')


@db_connection_decorator
def update_data_in_table(cursor, table, user_id, new_name):
    """
    Update the name of a row in the specified table based on the provided user ID.
    Args:
        cursor (sqlite3.Connection): The SQLite database connection.
        table (str): The name of the table to update.
        user_id (int): The ID of the user whose name needs to be updated.
        new_name (str): The new name to set for the user.
    """
    cursor.execute(f'UPDATE {table} SET Name = ? WHERE Id = ?', (new_name, user_id))
    my_logger.info(f'Name updated successfully in {table}')


def add_data_from_csv(path, add_data_function):
    """
    Add data from a CSV file to the database using the specified add_function.
    Args:
        path (str): The path to the CSV file containing data.
        add_data_function (function): The function to add data to the database.
    """
    with open(path, 'r') as csvfile:
        reader = list(csv.DictReader(csvfile))
        return add_data_function(reader)


@db_connection_decorator
def modify_row(cursor, table_name, input_id, new_data):
    """
    Modify a row in the specified table_name based on the provided parameters.
    Args:
        cursor (sqlite3.Cursor): The SQLite database cursor.
        table_name (str): The name of the table_name to modify.
        input_id (int, optional): The ID of the to modify (default: None).
        new_data (dict): A dictionary containing the new data to update.
    """
    if not new_data:
        my_logger.warning('No new data provided for update')
        return

    query_parts = ', '.join([f'{key} = "{value}"' if isinstance(value, str) else f'{key} = {value}'
                             for key, value in new_data.items()])
    query = f'UPDATE {table_name} SET {query_parts} WHERE Id = {input_id}'

    cursor.execute(query)
    my_logger.info(f'Row in {table_name} modified successfully')


@db_connection_decorator
def delete_if_exists(cursor, table_name, condition):
    """
    Delete rows from the specified table based on the given condition.
    Args:
        cursor (sqlite3.Cursor): The database cursor to execute the DELETE query.
        table_name (str): The name of the table from which to delete rows.
        condition (str): The condition that determines which rows to delete.
    Returns:
        None
    """
    cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
    if cursor.rowcount > 0:
        my_logger.info(f'Row with {condition} deleted from {table_name}')
    else:
        my_logger.warning(f'Row with {condition} not found in {table_name}')


def delete_row(table_name, condition):
    """
    Delete rows from the specified table based on the given condition.
    Args:
        table_name (str): The name of the table from which to delete rows.
        condition (str): The condition that determines which rows to delete.
    Returns:
        None
    """
    delete_if_exists(table_name, condition)
