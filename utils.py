import random


def get_int(var):
    while True:
        try:
            return int(input(f'Enter integer number of {var}: '))
        except ValueError:
            print('Invalid value!')


def generate_random_matrix(num_rows, num_columns, min_value=-50, max_value=200):
    return [[random.randint(min_value, max_value) for _ in range(num_columns)] for _ in range(num_rows)]


def print_matrix(matrix):
    print('Matrix:')
    for sublist in matrix:
        print(sublist)
    print(end='\n\n')
