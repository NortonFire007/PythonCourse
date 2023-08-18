from db_decorator import db_connection_decorator
from logger import setup_logger
from datetime import datetime, timezone
import requests
from create_api_module import modify_row

API_KEY = 'fca_live_4uqhXfyZENDdm83mAzfXYpguR4kCOXDt76l5cEIl'
URL = f'https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}'

my_logger = setup_logger()


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
def perform_money_transfer(cursor, sender_account_number, receiver_account_number, amount):
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

    if sender_account[6] < amount:
        my_logger.warning("There are not enough funds on the sender's account")
        return 'Insufficient balance'

    if sender_account[5] != receiver_account[5]:
        converted_amount = convert_currency(sender_account[5], receiver_account[5], amount)
        if converted_amount is None:
            return 'Currency conversion error'
    else:
        converted_amount = amount

    modify_row(table='Account', account_id=sender_account[0],
               new_data={'Amount': sender_account[6] - amount})
    modify_row(table='Account', account_id=receiver_account[0],
               new_data={'Amount': receiver_account[6] + converted_amount})

    cursor.execute('INSERT INTO TransactionTable (Bank_sender_name, Account_sender_id, '
                   'Bank_receiver_name, Account_receiver_id, Sent_Currency, Sent_Amount, Datetime) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (sender_account[4], sender_account[1], receiver_account[0], receiver_account[1],
                    converted_amount, receiver_account[5],
                    datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))

    my_logger.info('Money transfer successful')
    return 'Money transfer successful'
