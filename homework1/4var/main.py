# Вариант 4
# Дана целочисленная квадратная матрица. Определить:
# 1) произведение элементов в тех строках, которые не содержат отрицательных элементов;
# 2) максимум среди сумм элементов диагоналей, параллельных главной диагонали матрицы.
import random
import functools

from utils import get_rows_and_columns


def generate_random_matrix(num_rows, num_columns, min_value=-50, max_value=200):
    matrix = []
    for i in range(num_rows):
        row = [random.randint(min_value, max_value) for _ in range(num_columns)]
        matrix.append(row)
    return matrix


def multiply_list_numbers(my_list):
    result = functools.reduce(lambda a, b: a * b, my_list)
    return result


def sum_diagonal_parallel(matrix):
    diagonal_sum_ = [sum([matrix[(4 - k if k < 4 else 0) + d][(0 if k < 4 else 4 - (k % 4)) + d] for d in range(k % 4)])
                     for k in range(1, 8) if k != 4]
    return diagonal_sum_


rows = get_rows_and_columns('rows')
columns = get_rows_and_columns('columns')

random_matrix = generate_random_matrix(rows, columns)

print('Matrix:')
# for sublist in random_matrix:
print(*random_matrix, sep='\n')
print('\n')

for sublist in random_matrix:
    print(sublist)# enumerate + comprehension
    if any(num < 0 for num in sublist):
        print('Contain negative numbers in this row.')
    else:
        product = multiply_list_numbers(sublist)
        print('Product of positive numbers in sublist:', product)

diagonal_sum_answer = sum_diagonal_parallel(random_matrix)
print(*diagonal_sum_answer, sep='\n')
