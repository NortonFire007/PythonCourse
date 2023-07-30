# Вариант 13
# Осуществить циклический сдвиг элементов прямоугольной матрицы на n элементов вправо или
# вниз (в зависимости от введенного режима), n может быть больше количества элементов в строке
# или столбце.
import random

ROWS = 4
COLUMNS = 6


def get_valid_word(allowed_words):
    while True:
        try:
            word = input(f'Input the direction ({", ".join(allowed_words)}): ')
            if word in allowed_words:
                return word
        except ValueError:
            print('Please enter a string.')


directions_words = ('down', 'right')
direction = get_valid_word(directions_words)
print("Direction:", direction)


def get_valid_integer_input(num):
    while True:
        try:
            value = int(input(num))
            return value
        except ValueError:
            print('Please enter a valid integer number.')


n = get_valid_integer_input('Input n: ')


def generate_random_matrix(num_rows, num_columns, min_value=-50, max_value=200):
    matrix = []
    for i in range(num_rows):
        row = [random.randint(min_value, max_value) for _ in range(num_columns)]
        matrix.append(row)
    return matrix


matrix1 = generate_random_matrix(ROWS, COLUMNS)

for i in matrix1:
    print(i)

print('')


def cyclic_shift_down(my_list, num_to_shift):
    if len(my_list) <= 1:
        return my_list
    return [*my_list[-num_to_shift:], *my_list[:-num_to_shift]]


def cyclic_shift_right(my_list, num_to_shift):
    return [cyclic_shift_down(sublist, num_to_shift) for sublist in my_list]


if direction == 'down':
    matrix1 = cyclic_shift_down(matrix1, n)
elif direction == 'right':
    matrix1 = cyclic_shift_right(matrix1, n)
else:
    print('\nError!')

for i in matrix1:
    print(i)
