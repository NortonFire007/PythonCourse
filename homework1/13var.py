# Вариант 13
# осуществить циклический сдвиг элементов прямоугольной матрицы на n элементов вправо или
# вниз (в зависимости от введенного режима), n может быть больше количества элементов в строке
# или столбце.
from utils import get_int, generate_random_matrix, print_matrix

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

n = get_int('n')

matrix1 = generate_random_matrix(ROWS, COLUMNS)

print_matrix(matrix1)


def cyclic_shift_down(my_list, num_to_shift):
    if len(my_list) <= 1:
        return my_list
    return [*my_list[-num_to_shift:], *my_list[:-num_to_shift]]


def cyclic_shift_right(my_list, num_to_shift):
    return [cyclic_shift_down(sublist, num_to_shift) for sublist in my_list]


if direction == 'down':
    matrix1 = cyclic_shift_down(matrix1, n)
else:
    matrix1 = cyclic_shift_right(matrix1, n)

print_matrix(matrix1)
