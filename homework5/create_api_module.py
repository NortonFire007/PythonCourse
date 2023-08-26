import sqlite3
import csv
from logger import setup_logger
from db_decorator import db_connection_decorator
from validation import valid_full_name, validate_strict_account_fields, validate_account_number

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
    # ids = random.sample(range(1, 10001), len(input_data))
    data = input_data[0] if isinstance(input_data[0], list) else input_data
    # rows = [(i, *valid_full_name(row['user_full_name']), row['birth_day'], row['accounts'])
    #         for i, row in zip(ids, data)]
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

# @db_connection_decorator
# def get_account_by_number(cursor, account_number):
#     """
#       Retrieve account information based on the account number.
#
#       This function queries the database to fetch account information associated with the given account number.
#
#       Args:
#           cursor (sqlite3.Cursor): The database cursor to execute SQL queries.
#           account_number (str): The account number for which to retrieve account information.
#
#       Returns:
#           tuple or str: If the account is found in the database, a tuple containing account information is returned.
#                         If the account is not found, a warning is logged and an error message is returned.
#       """
#     cursor.execute('SELECT * FROM Account WHERE Account_Number = ?', (account_number,))
#     account_row = cursor.fetchone()
#
#     if account_row:
#         return account_row
#     else:
#         my_logger.warning(f"The account data by account number {account_number} wasn't received!")
#         return f"The account data by account number {account_number} wasn't received!"


# def convert_currency(from_currency, to_currency, amount):
#     exchange_rate = freecurrencyapi.Client(API_KEY).latest()['data'][to_currency]
#     return round(amount * exchange_rate, 2)


# def convert_currency(from_currency, to_currency, amount):
#     """
#      Convert an amount of money from one currency to another.
#
#      This function uses an external API to fetch the current exchange rates between the given currencies,
#      calculates the equivalent amount in the destination currency, and returns the result rounded to two decimal places.
#
#      Args:
#          from_currency (str): The currency code of the source currency.
#          to_currency (str): The currency code of the target currency.
#          amount (float): The amount of money to be converted.
#
#      Returns:
#          float: The equivalent amount in the target currency after conversion.
#      Raises:
#          KeyError: If the API response does not contain the necessary exchange rate information.
#          ValueError: If the API response or exchange rate calculation encounters an error.
#      """
#     response = requests.get(f'{URL}&currencies={from_currency}%2C{to_currency}').json()
#     print('response', response)
#     print('URL:', f'{URL}&currencies={from_currency}%2C{to_currency}&base_currency={from_currency}')
#     exchange_rate = response['data'][to_currency]
#     return round(amount * exchange_rate, 2)

# @db_connection_decorator
# def perform_money_transfer(cursor, sender_account_number, receiver_account_number, amount, time=None):
#     """
#        Perform a money transfer between two accounts.
#
#        This function transfers the specified amount of money from the sender's account to the receiver's account.
#        It performs necessary checks on the sender's account balance, currency compatibility, and updates the account
#        balances accordingly. It also logs the transaction details.
#
#        Args:
#            cursor (sqlite3.Cursor): The database cursor to execute SQL queries.
#            sender_account_number (str): The account number of the sender.
#            receiver_account_number (str): The account number of the receiver.
#            amount (float): The amount of money to be transferred.
#            time (optional) : format ('%Y-%m-%d %H:%M:%S') transaction time
#
#        Returns:
#            str: A string indicating the result of the money transfer operation. Possible values include:
#                - 'Invalid account numbers': If either the sender's or receiver's account is invalid.
#                - 'Insufficient balance': If the sender's account does not have enough funds.
#                - 'Currency conversion error': If currency conversion fails.
#                - 'Money transfer successful': If the money transfer is successful.
#        """
#     sender_account = get_account_by_number(sender_account_number)
#     receiver_account = get_account_by_number(receiver_account_number)
#
#     if not sender_account or not receiver_account:
#         my_logger.warning('Invalid account numbers')
#         return 'Invalid account numbers'
#
#     elif sender_account[6] < amount:
#         my_logger.warning("There are not enough funds on the sender's account")
#         return 'Insufficient balance'
#
#     elif sender_account[5] != receiver_account[5]:
#         converted_amount = convert_currency(sender_account[5], receiver_account[5], amount)
#         if converted_amount is None:
#             return 'Currency conversion error'
#     else:
#         converted_amount = amount
#
#     modify_row('Account', sender_account[0],
#                new_data={'Amount': sender_account[6] - amount})
#     modify_row('Account', receiver_account[0],
#                new_data={'Amount': receiver_account[6] + converted_amount})
#
#     cursor.execute('SELECT Name FROM Bank WHERE Id = ?', (sender_account[4],))
#     bank_sender_name = cursor.fetchone()
#     cursor.execute('SELECT Name FROM Bank WHERE Id = ?', (receiver_account[4],))
#     bank_receiver_name = cursor.fetchone()
#
#     if time is None:
#         time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
#
#     cursor.execute('INSERT INTO TransactionTable (Bank_sender_name, Account_sender_id, '
#                    'Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) '
#                    'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                    (bank_sender_name[0], sender_account[1], bank_receiver_name[0], receiver_account[1],
#                     converted_amount, receiver_account[5], time))
#
#     my_logger.info('Money transfer successful')
#     return 'Money transfer successful'


# def main():
#     users = [
#         {'id': 5385, 'user_full_name': 'John O', 'birth_day': '1992-03-17', 'accounts': 'ID--r5-gry-70325-g'},
#         {'id': 9064, 'user_full_name': 'Jane Babel', 'birth_day': '1984-07-10', 'accounts': 'ID--a1-b-123456-x7'}
#     ]
#
#     banks_data = [
#         {'name': 'Bank Ad', 'id': 31},
#         {'name': 'Bank B', 'id': 73}
#     ]
#
#     accounts_data = [
#         {'user_id': 5777, 'type': 'debit', 'account_number': 'ID--h5-i-567890-q2', 'bank_id': 1, 'currency': 'USD',
#          'amount': 5000, 'status': 'silver'},
#         {'user_id': 503, 'type': 'credit', 'account_number': 'ID--j3-q-432547-u9', 'bank_id': 2, 'currency': 'EUR',
#          'amount': 10000, 'status': 'gold'}
#     ]
#
#     add_user(users)
#     add_bank(banks_data)
#     add_account(accounts_data)
#
#     add_data_from_csv('banks.csv', add_bank)
#     add_data_from_csv('accounts.csv', add_account)
#     add_data_from_csv('users.csv', add_user)
#
#     modify_row('Account', 7, {'Amount': 8750})
#     modify_row('Bank', 57, {'Id': 56, 'Name': 'New Bank Name'})
#     delete_row('User', 'Id = 6')
#
#     perform_money_transfer('ID--r5-gry-70325-g', 'ID--u0-vuv-6819-u1', 150)
#     perform_money_transfer('ID--j3-q-432547-u9', 'ID--f4-ggg-90123-g', 3200, '2022-08-19 11:42:24')
#     perform_money_transfer('ID--j3-q-432547-u9', 'ID--u0-vuv-6819-u1', 1500)
#     perform_money_transfer('ID--f4-ggg-90123-g', 'ID--u0-vuv-6819-u1', 15000)
#
#
# if __name__ == "__main__":
#     main()
