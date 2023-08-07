import os
import logging
import csv
import requests
import argparse

URL = 'https://randomuser.me/api/?results=5000&format=csv'


# def setup_logger(log_file, log_level=logging.DEBUG):
#     logger = logging.getLogger("my_logger")
#     logger.setLevel(log_level)
#
#     file_handler = logging.FileHandler(log_file)
#     file_handler.setLevel(log_level)
#
#     formatter = logging.Formatter(
#         "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
#     )
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#     return logger

def setup_logger(log_level=logging.DEBUG):
    logging.basicConfig(
        filename='my_log_file.log',
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s"'
        # format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    )
    return logging.getLogger('my_logger')


# def download_user_accounts_csv(url, output_csv, my_logger):
#     my_logger.info('Downloading user accounts data from the API...')
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.text
#         if data:
#             my_logger.info(f'Received {len(data)} user accounts from the API.')
#             with open(output_csv, 'w', newline='') as file:
#                 file.write(data)
#             my_logger.info('Successfully downloaded user accounts to user_accounts.csv')
#         else:
#             my_logger.warning('No data received from the API.')
#     else:
#         my_logger.error(f'Failed to fetch data. Status code: {response.status_code}')
def download_user_accounts_csv(output_csv, my_logger):
    my_logger.info('Downloading user accounts data from the API...')
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        file.write((requests.get(URL)).text)
    my_logger.info('Successfully downloaded user accounts to user_accounts.csv')


def read_data_from_csv():  # file_path
    with open('user_accounts_csv.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def write_data_in_csv(file_path, data1):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = list(data1[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data1)


def count_lines_in_csv(file_path):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        line_count = sum(1 for _ in reader)
    return line_count


def add_fields_to_the_file(csv_file):
    # with open(csv_file, 'a', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow()
    data_to_append = []
    # data_to_append.append(count_lines_in_csv(file_path))


def filter_data(data1, my_logger, gender=None, num_rows=None):
    filtered_data = []
    if gender:
        filtered_data = [user for user in data1 if user['gender'] == gender]
        # data1 = list(filter(lambda x: x['gender'] == gender, data1))
        my_logger.info('The data was filtered by gender')
    if num_rows and num_rows < len(data1):
        filtered_data = data1[:num_rows]
        my_logger.info('The data was filtered by num_rows')
    else:
        my_logger.warning('The data was not filtered by any of the parameters!!!')
    return filtered_data


def change_content(field, data):  # name.title
    rule_list = [{'Mrs': 'missis'}, {'Ms ': 'miss'}, {'Mr': 'mister'}, {'Madame': 'mademoiselle'}]



def main(output_folder, output_filename, log_lev, gender=None, num_rows=None):
    # print("Current working directory:", os.getcwd()) E:\Programming\pythonProj\pythonProject\PythonCourse\Homework3
    my_logger = setup_logger(log_lev)

    download_user_accounts_csv('user_accounts_csv.csv', my_logger)
    print(f"Destination folder: {output_folder}")
    print(f"Filename: {output_filename}")
    print(f"Gender filter: {gender}")
    print(f"Number of rows filter: {num_rows}")
    print(f"Log level: {log_lev}")

    data = read_data_from_csv()  # 'user_accounts.csv'
    print(data)

    filterted_data = filter_data(data, my_logger, gender, num_rows)
    print(filterted_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and filter user accounts data.')
    parser.add_argument('--output_folder', type=str,
                        help='Path to the destination folder where output file will be placed.')
    parser.add_argument('--output_filename', default='output', type=str, help='Output filename (default: output)')
    # parser.add_mutually_exclusive_group()
    parser.add_argument('--gender', choices=['male', 'female'], type=str,
                        help='Filter data by gender (male or female).')
    parser.add_argument('--num_rows', type=int, help='Filter data by number of rows.')
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str, help='Log level (default: INFO).')

    args = parser.parse_args()
    log_level = getattr(logging, args.log_level.upper())

    main(args.output_folder, args.output_filename, log_level, args.gender, args.num_rows)
