# Вариант 4
# Дана целочисленная квадратная матрица. Определить:
# 1) произведение элементов в тех строках, которые не содержат отрицательных элементов;
# 2) максимум среди сумм элементов диагоналей, параллельных главной диагонали матрицы.
import functools
from utils import get_int, generate_random_matrix, print_matrix


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
