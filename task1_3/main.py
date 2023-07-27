# Вариант 13
# Осуществить циклический сдвиг элементов прямоугольной матрицы на n элементов вправо или
# вниз (в зависимости от введенного режима), n может быть больше количества элементов в строке
# или столбце.
import random

ROWS = 4
COLUMNS = 6

while True:
    try:
        direction = int(input('Input the direction to shift(left - 1 or right - 2): '))
        if 0 < direction < 3:
            break

    except ValueError:
        print('Please enter a string.')

while True:
    try:
        n = int(input('Input n: '))
        break
    except ValueError:
        print('Please enter a valid integer number.')


def create_random_matrix(num_rows, num_columns):
    matrix = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    for i in range(num_rows):
        for j in range(num_columns):
            matrix[i][j] = random.randint(-50, 90)
    return matrix


matrix1 = create_random_matrix(ROWS, COLUMNS)

for i in matrix1:
    print(i)

print("")


def cyclic_shift_down(my_list, num_to_shift):
    if len(my_list) <= 1:
        return my_list

    last_elements = my_list[-num_to_shift:]
    last_elements.extend(my_list[:-num_to_shift])

    return last_elements


def cyclic_shift_right(my_list, num_to_shift):
    updated_list = [cyclic_shift_down(sublist, num_to_shift) for sublist in my_list]

    return updated_list


if direction == 1:
    matrix1 = cyclic_shift_down(matrix1, n)
else:
    matrix1 = cyclic_shift_right(matrix1, n)

for i in matrix1:
    print(i)
