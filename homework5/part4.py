import random
from db_decorator import db_connection_decorator
from logger import setup_logger
from datetime import datetime, timedelta
from create_api_module import delete_row
from money_transfer import convert_currency

DISCOUNT_LIST = [25, 30, 50]

my_logger = setup_logger()


@db_connection_decorator
def get_data_from_table(cursor, table_name, fields, condition=None):
    """
       Retrieve data from a database table based on the specified conditions.
       Args:
           cursor (sqlite3.Cursor): The database cursor.
           table_name (str): The name of the table to retrieve data from.
           fields (str): The fields/columns to select from the table.
           condition (str, optional): The condition to filter the data (default is None).
       Returns:
           list: A list of tuples containing the retrieved data.
       """
    cursor.execute(f'SELECT {fields} FROM {table_name} WHERE {condition}') if condition \
        else cursor.execute(f'SELECT {fields} FROM {table_name}')
    return cursor.fetchall()


def randomly_choose_users_for_discount():
    """
       Randomly selects a subset of users from the database to receive discounts.
       Returns:
           list: A list of tuples containing user IDs and randomly chosen discounts.
       """
    row_count = get_data_from_table('User', 'MIN(COUNT(*), 10)')
    number_of_users = random.randint(1, row_count[0][0])

    rows = get_data_from_table('User', '*')
    id_list = [row[0] for row in rows]
    random_sample = random.sample(id_list, number_of_users)
    return [(e, random.choice(DISCOUNT_LIST)) for e in random_sample]


def get_debtors_names():
    """
      Retrieves the names of users who have debts based on account balances.
      Returns:
          list: A list of usernames who have debts.
      """
    accounts = get_data_from_table('Account', 'Account_Number', 'amount < 0')
    if accounts:
        accounts_debtors_list = [row[0] for row in accounts]

        result = get_data_from_table('User', 'Name, Surname, Accounts')
        debtors_names = [' '.join(i[:2]) for i in result for j in str(i[2]).split(', ') if j in accounts_debtors_list]

        my_logger.info(f'Users who have debts: {debtors_names}!!!')
        return debtors_names
    else:
        my_logger.info(f'Users who have debts not found.')


def get_bank_with_the_biggest_capital():
    """
    Retrieves the bank with the highest capital in USD.
    Returns:
        list: A list containing the name(s) of the bank(s) with the highest capital.
    """
    result = get_data_from_table('Account', 'Bank_id, Amount, Currency')
    converted_currency = [(r[0], convert_currency(r[2], 'USD', r[1])) for r in result]
    max_amount = max(converted_currency, key=lambda item: item[1])
    result = get_data_from_table('Bank', 'Id, Name')
    return [r[1] for r in result if r[0] == max_amount[0]]


@db_connection_decorator
def get_the_oldest_client_bank(cursor):
    """
       Retrieves the bank(s) that serve the oldest client based on their birthdate.
       Args:
           cursor (sqlite3.Cursor): The database cursor to execute the SQL queries.
       Returns:
           list: A list containing the name(s) of the bank(s) that serve the oldest client.
       """
    dates = get_data_from_table('User', 'Birth_day')
    oldest_date = min(dates, key=lambda x: x[0])
    accounts = get_data_from_table(f'User', 'Accounts', f'birth_day ="{oldest_date[0]}"')
    result = accounts[0][0].split(', ')
    query = """
    SELECT Bank_id
    FROM Account
    WHERE account_number IN ({})
    """.format(', '.join(['?'] * len(result)))

    cursor.execute(query, result)
    ans = cursor.fetchall()
    ans = [i[0] for i in ans]
    query = """
        SELECT Name
        FROM Bank
        WHERE id IN ({})
    """.format(', '.join(['?'] * len(ans)))

    cursor.execute(query, [sublist for sublist in ans])
    bank_names = cursor.fetchall()
    bank_names = [i[0] for i in bank_names]
    my_logger.info(f'{bank_names} - banks which serves the oldest client.')
    return bank_names


def delete_accounts_and_users_without_full_info():
    """ Deletes user accounts and users that have missing or empty information fields. """
    delete_row('User', "Name IS NULL OR Name = '' OR Surname IS NULL OR Birth_day IS NULL OR Birth_day = '' ")
    account_data = get_data_from_table('User', 'id')
    unique_user_ids = [item[0] for item in account_data]
    user_ids_str = ', '.join(map(str, unique_user_ids))
    delete_row('Account', f'user_id NOT IN ({user_ids_str})')


def get_user_last_three_months_transactions(user_id):
    """
        Get transactions of a particular user for the last three months.
        Args:
            user_id (int): The user ID for which to retrieve transactions.
        Returns:
            list: List of transactions for the user in the last three months.
        """
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    return get_data_from_table('TransactionTable', '*',
                               f"Account_sender_id = {user_id} AND Datetime >= '{three_months_ago}'")


def get_bank_with_highest_unique_outbound_users():
    """
     Get the bank with the highest number of unique users who performed outbound transactions.
     Returns:
         str: Name of the bank with the highest number of unique users for outbound transactions.
     """
    transactions_data = get_data_from_table('TransactionTable', 'Bank_sender_name, Account_sender_id')

    bank_id_counts = {}

    for bank, bank_id in transactions_data:
        if bank not in bank_id_counts:
            bank_id_counts[bank] = set()
        bank_id_counts[bank].add(bank_id)

    max_bank = max(bank_id_counts.items(), key=lambda x: len(x[1]))

    my_logger.info(f'Bank with the highest number of unique users performed outbound transactions is {max_bank[0]}')
    return max_bank[0]
