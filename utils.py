

def get_rows_and_columns(param):
    while True:
        try:
            return int(input(f'Enter the number of {param}: '))
        except ValueError:
            print("Please enter valid integer values for rows and columns.")