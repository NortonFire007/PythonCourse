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
    cursor.close()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an initial database structure.')
    parser.add_argument('--uniqueness', action='store_true')
    args = parser.parse_args()

    create_database(args.uniqueness)
