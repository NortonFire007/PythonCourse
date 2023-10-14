# Вариант 12
# уплотнить заданную матрицу, удаляя из нее строки и столбцы, заполненные нулями. Найти номер
# первой из строк, содержащих хотя бы один положительный элемент.

from utils import get_int, generate_random_matrix, print_matrix

rows = get_int('rows')
columns = get_int('columns')

matrix1 = generate_random_matrix(rows, columns, -20, 10)

print_matrix(matrix1)


def remove_rows_and_columns(matrix, value):
    rows_to_delete = []
    columns_to_delete = set()

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == value:
                rows_to_delete.append(i)
                columns_to_delete.add(j)
    return [
        [sub_val for j, sub_val in enumerate(val) if j not in columns_to_delete]
        for i, val in enumerate(matrix) if i not in rows_to_delete
    ]


matrix1 = remove_rows_and_columns(matrix1, 0)

print_matrix(matrix1)


def find_positive_number(matrix):
    return next((f'Num: {i + 1}' for i, val in enumerate(matrix) if any(num > 0 for num in val)),
                'There are no positive numbers in the matrix')


print(find_positive_number(matrix1))
