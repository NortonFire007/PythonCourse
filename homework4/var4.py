import functools
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


def multiply_list_numbers(my_list):
    return functools.reduce(lambda a, b: a * b, my_list)


def sum_diagonal_parallel(matrix, size):
    return [sum([matrix[(size - k if k < size else 0) + d][
                     (0 if k < size else size - (k % size)) + d] for d in
                 range(k % size)])
            for k in range(1, size * 2) if k != size]


def find_positive_row(mass):
    for sublist in mass:
        print(sublist)
        if any(num < 0 for num in sublist):
            print('Contains of negative numbers in this row.')
        else:
            product = multiply_list_numbers(sublist)
            print('Product of positive numbers in sublist:', product)


def main():
    size = get_int('size')

    random_matrix = generate_random_matrix(size, size)

    print_matrix(random_matrix)

    find_positive_row(random_matrix)

    diagonal_sum_answer = sum_diagonal_parallel(random_matrix, size)
    print(*diagonal_sum_answer, sep='\n')


if __name__ == '__main__':
    main()
