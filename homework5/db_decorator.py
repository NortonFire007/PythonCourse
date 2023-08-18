import sqlite3
import os
from functools import wraps
from initial_db_setup_001 import create_database


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
        cursor = conn.cursor()
        result = func(cursor, *args, **kwargs)
        conn.commit()
        conn.close()
        return result

    return wrap_the_function
