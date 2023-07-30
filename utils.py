import random


def get_rows_and_columns():
    while True:
        try:
            rows = int(input('Enter the number of rows: '))
            columns = int(input('Enter the number of columns: '))
            return rows, columns
        except ValueError:
            print("Please enter valid integer values for rows and columns.")


def create_random_matrix(num_rows, num_columns):
    matrix = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    for i in range(num_rows):
        for j in range(num_columns):
            matrix[i][j] = random.randint(-50, 5)
    return matrix
