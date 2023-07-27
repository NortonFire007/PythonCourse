# Вариант 4
# Дана целочисленная квадратная матрица. Определить:
# 1) произведение элементов в тех строках, которые не содержат отрицательных элементов;
# 2) максимум среди сумм элементов диагоналей, параллельных главной диагонали матрицы.
import random


def create_random_matrix(num_rows, num_columns):
    matrix = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
    for i in range(num_rows):
        for j in range(num_columns):
            # matrix[i][j] = random.choice([-1, 1]) * random.randint(1, 100)
            matrix[i][j] = random.randint(-50, 200)
    return matrix


def multiply_list_numbers(my_list):
    result = 1
    for num in my_list:
        result *= num
    return result


def sum_diagonal_parallel(matrix):
    diagonal_sum = []

    for j in range(1, rows):
        value = 0
        k = 0
        while j + k < columns and k < rows:
            value += matrix[k][j + k]
            # print("\n value: ", value)
            k += 1
        diagonal_sum.append(value)

    for i in range(1, rows):
        value = k = 0
        while i + k < rows and k < columns:
            value += matrix[i + k][k]
            # print("\n value: ", value)
            k += 1
        diagonal_sum.append(value)

    return diagonal_sum


while True:
    try:
        rows = int(input('Enter the number of rows: '))
        columns = int(input('Enter the number of columns: '))
        break
    except ValueError:
        print("Please enter a valid integer number.")

random_matrix = create_random_matrix(rows, columns)

print('Matrix:')
for sublist in random_matrix:
    print(sublist)
print("")

for sublist in random_matrix:
    print(sublist)
    if any(num < 0 for num in sublist):
        print('Contains of negative numbers in this row.')
    else:
        product = multiply_list_numbers(sublist)
        print('Product of positive numbers in sublist:', product)

# for sublist in random_matrix:
#     print(sublist)
#     if all(num > 0 for num in sublist):
#         product = multiply_list_numbers(sublist)
#         print("Product of positive numbers in sublist:", product)

# for j in random_matrix[0][1:]:
#    sum_diagonal_parallel_base = 0
#    k = 0
#    while True:
#        if j + k < len(random_matrix[0]) and  k < len(random_matrix[0]):
#          sum_diagonal_parallel_base += random_matrix[k][j + k]
#          k+=1
#        else:
#            break
#    print(sum_diagonal_parallel_base)

# test_matrix = [
#     [-11, 91, 56, -8],
#     [-43, 32, 47, 158],
#     [-17, 139, -39, 57]
# ]

diagonal_sum_answer = sum_diagonal_parallel(random_matrix)
if len(diagonal_sum_answer) == 0:
    print("\n List diagonal_sum_answer is empty! ")
else:
    print("\n diagonal_sum: ", diagonal_sum_answer)
