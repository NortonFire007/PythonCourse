import sqlite3
import argparse


# PART 1.
def create_database(uniqueness):
    conn = sqlite3.connect('my_data.db')

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Bank (
                    Id INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL UNIQUE
                )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TransactionTable (
                    Id INTEGER PRIMARY KEY,
                    Bank_sender_name TEXT NOT NULL,
                    Account_sender_id TEXT NOT NULL,
                    Bank_receiver_name TEXT NOT NULL,
                    Account_receiver_id TEXT NOT NULL,
                    Sent_Currency TEXT NOT NULL,
                    Sent_Amount REAL NOT NULL,
                    Datetime TEXT
                )''')

    user_name_constraint, user_surname_constraint = ('UNIQUE', 'UNIQUE') if uniqueness else ('', '')

    cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                    Id INTEGER PRIMARY KEY,
                    Name TEXT NOT NULL {name_constraint},
                    Surname TEXT NOT NULL {surname_constraint},
                    Birth_day INTEGER,
                    Accounts TEXT NOT NULL
                )'''.format(name_constraint=user_name_constraint, surname_constraint=user_surname_constraint))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            Id INTEGER PRIMARY KEY,
            User_id INTEGER NOT NULL,
            Type TEXT NOT NULL,
            Account_Number TEXT NOT NULL UNIQUE,
            Bank_id INTEGER NOT NULL,
            Currency TEXT NOT NULL,
            Amount REAL NOT NULL,
            Status TEXT CHECK(Status IN ('gold', 'silver', 'platinum')), -- CHECK constraint,
            FOREIGN KEY (User_id) REFERENCES User (Id),
            FOREIGN KEY (Bank_id) REFERENCES Bank (id)
        )''')

    conn.commit()

    # bank_data = [(46, 'PrivatBank'), (17, 'AlphaBank'), (93, 'Monobank')]
    # cursor.executemany('INSERT INTO Bank (Id, Name) VALUES (?, ?)', bank_data)
    #
    # transaction_data = [('AlphaBank', 'Account1', 'PrivatBank', 'Account2', 'USD', 100.0, '2023-08-01'),
    #                     ('Monobank', 'Account3', 'Monobank', 'Account1', 'EUR', 150.0, '2023-08-02')]
    # cursor.executemany(
    #     'INSERT INTO TransactionTable '
    #     '(Bank_sender_name, Account_sender_id, Bank_receiver_name, Account_receiver_id, Sent_Currency, '
    #     'Sent_Amount, Datetime) VALUES(?, ?, ?, ?, ?, ?, ?)', transaction_data)
    #
    # users = [('User1', 'Surname1', 1990, 'Account1, Account2'), ('User2', 'Surname2', 1985, 'Account3'),
    #          ('User3', 'Surname3', 2000, 'Account4, Account5')]
    # cursor.executemany('INSERT INTO User (Name, Surname, Birth_day, Accounts) VALUES (?, ?, ?, ?)', users)
    #
    # accounts = [
    #     (1, 'credit', '1234567890', 1, 'USD', 1000.0, 'gold'),
    #     (2, 'debit', '9876543210', 2, 'EUR', 500.0, 'silver'),
    #     (3, 'debit', '9876573210', 3, 'EUR', 500.0, 'silver')
    # ]
    # cursor.executemany('''INSERT INTO Account
    #                        (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status)
    #                        VALUES (?, ?, ?, ?, ?, ?, ?)''', accounts)
    #
    # cursor.execute('UPDATE User SET Name = "Bob" WHERE Birth_day = 1990')
    # cursor.execute('DELETE FROM Account WHERE Type = "credit" ')

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an initial database structure.')
    parser.add_argument('--uniqueness', action='store_true')
    args = parser.parse_args()

    create_database(args.uniqueness)
