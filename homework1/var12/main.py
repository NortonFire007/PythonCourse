# Вариант 12
# Уплотнить заданную матрицу, удаляя из нее строки и столбцы, заполненные нулями. Найти номер
# первой из строк, содержащих хотя бы один положительный элемент.
import random
from utils import get_rows_and_columns


def create_random_matrix(num_rows, num_columns):
    matrix = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    for i in range(num_rows):
        for j in range(num_columns):
            matrix[i][j] = random.randint(-50, 5)
    return matrix


rows, columns = get_rows_and_columns()

matrix1 = create_random_matrix(rows, columns)

print('Matrix:')
for sublist in matrix1:
    print(sublist)
print('\n')


def remove_rows_and_columns(matrix, value):
    rows_to_delete = []
    columns_to_delete = set()

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == value:
                rows_to_delete.append(i)
                columns_to_delete.add(j)

    new_matrix = [
        [sub_val for j, sub_val in enumerate(val) if j not in columns_to_delete]
        for i, val in enumerate(matrix) if i not in rows_to_delete
    ]

    return new_matrix


matrix1 = remove_rows_and_columns(matrix1, 0)

print('Matrix:')
for sublist in matrix1:
    print(sublist)
print('\n')


def find_positive_number(matrix):
    for i, val in enumerate(matrix, start=1):
        if any(num > 0 for num in val):
            return f'Num: {i}'
    return 'There are no positive numbers in the matrix'


print(find_positive_number(matrix1))
