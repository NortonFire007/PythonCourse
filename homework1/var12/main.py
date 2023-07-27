# Вариант 12
# Уплотнить заданную матрицу, удаляя из нее строки и столбцы, заполненные нулями. Найти номер
# первой из строк, содержащих хотя бы один положительный элемент.
import random


def create_random_matrix(num_rows, num_columns):
    matrix = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    for i in range(num_rows):
        for j in range(num_columns):
            matrix[i][j] = random.randint(-50, 5)
    return matrix


while True:
    try:
        rows = int(input('Enter the number of rows: '))
        columns = int(input('Enter the number of columns: '))
        break
    except ValueError:
        print("Please enter a valid integer number.")

matrix1 = create_random_matrix(rows, columns)

print('Matrix:')
for sublist in matrix1:
    print(sublist)
print("")


def remove_rows_and_columns(matrix, value):
    rows_to_delete = []
    columns_to_delete = []

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == value:
                rows_to_delete.append(i)
                columns_to_delete.append(j)

    new_matrix = [
        [matrix[i][j] for j in range(len(matrix[i])) if j not in columns_to_delete]
        for i in range(len(matrix))
        if i not in rows_to_delete
    ]

    return new_matrix


# test_matrix = [[-11, 91, 56, -8, 7],
#                [-43, 0, 4, 158, 4],
#                [-17, 139, -39, 57, 66],
#                [0, -4, 0, 4, 101],
#                [9, 28, 7, 18, -10]]

matrix1 = remove_rows_and_columns(matrix1, 0)

print('Matrix:')
for sublist in matrix1:
    print(sublist)
print("")


def find_positive_number(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] > 0:
                return i

    return -1


num = find_positive_number(matrix1)
if num > 0:
    print("Num: ", num + 1)
else:
    print("There are no positive numbers in the matrix")

# def delete_rows_or_columns_with_value_zero(matrix):
#     list_of_row_index_to_delete = []
#     new_matrix = []
#
#     for i in range(rows):
#         if all(matrix[i][j] != 0 for j in range(columns)):
#             list_of_row_index_to_delete.append(j)
#             new_matrix.append(matrix[i])
#
#
#     # new_matrix = [row for row in matrix if not any(element == 0 for element in row)]
#     # return new_matrix
#     # for i in range(rows - k):
#     #     for j in range(columns - k):
#     #         if matrix[i][j] == 0:
#     #             del matrix[i]
#     #     list_of_row_index_to_delete.append(j)
#     #     k += 1
#     # list_of_row_index_to_delete.append(element)
#     return new_matrix
