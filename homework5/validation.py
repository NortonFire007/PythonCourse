import re
from logger import setup_logger

my_logger = setup_logger()


def valid_full_name(full_name):
    """
      Cleans and validates a full name.

      This function takes a full name as input, removes any non-alphabet characters, and then splits the cleaned name
      into separate words using whitespace as the delimiter.

      Args:
          full_name (str): The full name to be cleaned and validated.

      Returns:
          list: A list of words from the cleaned full name, separated by whitespace.
      """
    cleaned_name = re.sub(r'[^a-zA-Z\s]', '', full_name)
    return re.split(r'\s+', cleaned_name.strip())


def validate_strict_account_fields(input_data):
    """
    Validate the fields 'type' and 'status' in the input data.
    Args:
        input_data (list of dict): List of dictionaries containing account information.
    Raises:
        ValueError: If any of the 'type' or 'status' values are not allowed.
    """
    allowed_types = ['credit', 'debit']
    allowed_statuses = ['gold', 'silver', 'platinum']

    for item in input_data:
        if item['type'] not in allowed_types:
            raise ValueError(f"Not allowed value '{item['type']}' for field 'Type'!")
        if item['status'] not in allowed_statuses:
            raise ValueError(f"Not allowed value '{item['status']}' for field 'Status'!")


def validate_account_number(account_number):
    account_number = re.sub(r'[#%_?&]', '-', account_number)
    """
    Validate the format of an account number.
    Args:
        account_number (str): Account number to be validated.
    Raises:
        ValueError: If the account number format is invalid.
    """
    if len(account_number) > 18:
        raise ValueError('Account number has too many chars!')
    elif len(account_number) < 18:
        raise ValueError('Account number has too little chars!')

    if not account_number.startswith('ID--'):
        raise ValueError("'Wrong format! Account number should start with 'ID--'!'")

    if not re.search(r'[a-zA-Z]{1,3}-\d+', account_number):
        raise ValueError('Broken ID!')

    my_logger.info(f'Account number {account_number} validation successful.')
