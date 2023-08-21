import sqlite3
import os
import requests
import csv
from logger import setup_logger
from db_decorator import db_connection_decorator
import freecurrencyapi
from datetime import datetime, timezone
from validation import valid_full_name, validate_strict_account_fields

API_KEY = 'fca_live_4uqhXfyZENDdm83mAzfXYpguR4kCOXDt76l5cEIl'
URL = f'https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}'

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
def add_user(cursor, *input_data):
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
    rows = [(name[0], name[1], row['birth_day'], row['accounts']) for row in data for name in
            [valid_full_name(row['user_full_name'])]]

    cursor.executemany('INSERT INTO User (Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?)', rows)
    my_logger.info('Users added successfully')


@db_connection_decorator
def add_bank(cursor, *input_data):
    """
    Add bank information to the database.
    Parameters:
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
        input_data: Account data to be added.

    Returns:
        None
    """

    validate_strict_account_fields(input_data)

    rows = prepare_rows(input_data)
    cursor.executemany('INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) VALUES '
                       '(?, ?, ?, ?, ?, ?, ?)', rows)
    my_logger.info('Accounts added to the database successfully')


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
        reader = list(csv.DictReader(csvfile))
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
        reader = list(csv.DictReader(csvfile))
        bank_data = [{'name': row['Bank'], 'id': row['Id']} for row in reader]
        return add_bank(bank_data)


def add_accounts_from_csv(path):
    """
    Add account data from a CSV file to the database.
    Args:
        path (str): The path to the CSV file containing account data.
    """
    with open(path, 'r') as csvfile:
        reader = list(csv.DictReader(csvfile))
        account_data = [{'user_id': row['User_id'], 'type': row['Type'], 'account_number': row['Account Number'],
                         'bank_id': row['Bank_id'], 'currency': row['Currency'], 'amount': row['Amount'],
                         'status': row['Status']} for row in reader]
        return add_account(account_data)


@db_connection_decorator
def modify_row(cursor, table, user_id=None, bank_id=None, account_id=None, new_data=None):
    """
    Modify a row in the specified table based on the provided parameters.
    Args:
        cursor (sqlite3.Cursor): The SQLite database cursor.
        table (str): The name of the table to modify.
        user_id (int, optional): The ID of the user to modify (default: None).
        bank_id (int, optional): The ID of the bank to modify (default: None).
        account_id (int, optional): The ID of the account to modify (default: None).
        new_data (dict): A dictionary containing the new data to update.
    """
    if not new_data:
        my_logger.warning('No new data provided for update')
        return

    id_column = 'Id'

    query_parts = [f' {key} = ?' for key in new_data.keys()]
    query = f'UPDATE {table} SET' + ','.join(query_parts) + f' WHERE {id_column} = ?'
    params = list(new_data.values())
    params.append(user_id if user_id else bank_id if bank_id else account_id)

    cursor.execute(query, params)
    my_logger.info(f'Row in {table} modified successfully')


@db_connection_decorator
def delete_row(cursor, table, row_id):
    """
    Delete a row from the specified table based on the provided row ID.
    Args:
        cursor (sqlite3.Cursor): The SQLite database cursor.
        table (str): The name of the table to delete from.
        row_id (int): The ID of the row to delete.
    """
    cursor.execute(f'SELECT * FROM {table} WHERE Id = ?', (row_id,))
    existing_row = cursor.fetchone()

    if not existing_row:
        my_logger.warning(f'Row with Id {row_id} not found in {table}')
        return

    cursor.execute(f'DELETE FROM {table} WHERE Id = ?', (row_id,))
    my_logger.info(f'Row with Id {row_id} deleted from {table}')


@db_connection_decorator
def get_account_by_number(cursor, account_number):
    """
      Retrieve account information based on the account number.

      This function queries the database to fetch account information associated with the given account number.

      Args:
          cursor (sqlite3.Cursor): The database cursor to execute SQL queries.
          account_number (str): The account number for which to retrieve account information.

      Returns:
          tuple or str: If the account is found in the database, a tuple containing account information is returned.
                        If the account is not found, a warning is logged and an error message is returned.
      """
    cursor.execute('SELECT * FROM Account WHERE Account_Number = ?', (account_number,))
    account_row = cursor.fetchone()

    if account_row:
        return account_row
    else:
        my_logger.warning(f"The account data by account number {account_number} wasn't received!")
        return f"The account data by account number {account_number} wasn't received!"


# def convert_currency(from_currency, to_currency, amount):
#     exchange_rate = freecurrencyapi.Client(API_KEY).latest()['data'][to_currency]
#     return round(amount * exchange_rate, 2)


def convert_currency(from_currency, to_currency, amount):
    """
     Convert an amount of money from one currency to another.

     This function uses an external API to fetch the current exchange rates between the given currencies,
     calculates the equivalent amount in the destination currency, and returns the result rounded to two decimal places.

     Args:
         from_currency (str): The currency code of the source currency.
         to_currency (str): The currency code of the target currency.
         amount (float): The amount of money to be converted.

     Returns:
         float: The equivalent amount in the target currency after conversion.
     Raises:
         KeyError: If the API response does not contain the necessary exchange rate information.
         ValueError: If the API response or exchange rate calculation encounters an error.
     """
    response = requests.get(f'{URL}&currencies={from_currency}%2C{to_currency}').json()
    exchange_rate = response['data'][to_currency]
    return round(amount * exchange_rate, 2)


@db_connection_decorator
def perform_money_transfer(cursor, sender_account_number, receiver_account_number, amount, time=None):
    """
       Perform a money transfer between two accounts.

       This function transfers the specified amount of money from the sender's account to the receiver's account.
       It performs necessary checks on the sender's account balance, currency compatibility, and updates the account
       balances accordingly. It also logs the transaction details.

       Args:
           cursor (sqlite3.Cursor): The database cursor to execute SQL queries.
           sender_account_number (str): The account number of the sender.
           receiver_account_number (str): The account number of the receiver.
           amount (float): The amount of money to be transferred.
           time

       Returns:
           str: A string indicating the result of the money transfer operation. Possible values include:
               - 'Invalid account numbers': If either the sender's or receiver's account is invalid.
               - 'Insufficient balance': If the sender's account does not have enough funds.
               - 'Currency conversion error': If currency conversion fails.
               - 'Money transfer successful': If the money transfer is successful.
       """
    sender_account = get_account_by_number(sender_account_number)
    receiver_account = get_account_by_number(receiver_account_number)

    if not sender_account or not receiver_account:
        my_logger.warning('Invalid account numbers')
        return 'Invalid account numbers'

    elif sender_account[6] < amount:
        my_logger.warning("There are not enough funds on the sender's account")
        return 'Insufficient balance'

    elif sender_account[5] != receiver_account[5]:
        converted_amount = convert_currency(sender_account[5], receiver_account[5], amount)
        if converted_amount is None:
            return 'Currency conversion error'
    else:
        converted_amount = amount

    modify_row(table='Account', account_id=sender_account[0],
               new_data={'Amount': sender_account[6] - amount})
    modify_row(table='Account', account_id=receiver_account[0],
               new_data={'Amount': receiver_account[6] + converted_amount})

    cursor.execute('SELECT Name FROM Bank WHERE Id = ?', (sender_account[4],))
    bank_sender_name = cursor.fetchone()
    cursor.execute('SELECT Name FROM Bank WHERE Id = ?', (receiver_account[4],))
    bank_receiver_name = cursor.fetchone()

    if not time:
        time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('INSERT INTO TransactionTable (Bank_sender_name, Account_sender_id, '
                   'Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (bank_sender_name[0], sender_account[1], bank_receiver_name[0], receiver_account[1],
                    converted_amount, receiver_account[5],
                    time))

    my_logger.info('Money transfer successful')
    return 'Money transfer successful'


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

perform_money_transfer(123456789, 567890123, 150)
perform_money_transfer(2471, 678901234, 2700, '2021-06-24 14:28:35')
