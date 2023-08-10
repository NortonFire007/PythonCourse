import os
import logging
import csv
from pprint import pprint
import requests
import argparse
import shutil
from datetime import datetime, timedelta
from statistics import mean
from collections import Counter

URL = 'https://randomuser.me/api/?results=5000&format=csv'


def setup_logger(log_level=logging.DEBUG):
    logging.basicConfig(
        filename='my_log_file.log',
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s"'
    )
    return logging.getLogger('my_logger')


def download_user_accounts_csv(output_csv, my_logger):
    my_logger.info('Downloading user accounts data from the API...')
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.text
        if data:
            my_logger.info(f'Received user accounts from the API.')
            with open(output_csv, 'w', newline='', encoding='utf-8') as file:
                file.write(data)
            my_logger.info('Successfully downloaded user accounts to user_accounts.csv')
        else:
            my_logger.warning('No data received from the API.')
    else:
        my_logger.error(f'Failed to fetch data. Status code: {response.status_code}')


def read_data_from_csv():
    with open('user_accounts_csv.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def write_data_in_csv(file_path, data1):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(data1[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data1)
        # my_logger.info(f'Data was written in {file_path}.')


def add_index_field(data1):
    for index, data in enumerate(data1, start=1):
        data['global_index'] = index
    return data1


def add_timezone_offset(datetime_str, offset_str):
    offset_parts = offset_str.split(':')
    hours = int(offset_parts[0])
    minutes = int(offset_parts[1])
    offset = timedelta(hours=hours, minutes=minutes)

    dt_with_offset = datetime_str + offset
    return dt_with_offset.strftime('%Y-%m-%d %H:%M:%S')


def add_current_time(data1):
    for data in data1:
        timezone_offset = data['location.timezone.offset']
        current_time = datetime.now()
        data['current_time'] = add_timezone_offset(current_time, timezone_offset)
    return data1


def change_name_content(data1):
    rule_list = {'Mrs': 'missis', 'Ms ': 'miss', 'Mr': 'mister', 'Madame': 'mademoiselle'}
    for data in data1:
        if data['name.title'] in rule_list:
            data['name.title'] = rule_list[data['name.title']]
    return data1


def convert_to_format(data1, field='dob.date', format_string='%Y-%m-%d'):
    for data in data1:
        dob = datetime.strptime(data[field], '%Y-%m-%dT%H:%M:%S.%fZ')
        data[field] = dob.strftime(format_string)
    return data1


def filter_data(data1, my_logger, gender=None, num_rows=None):
    filtered_data = []
    if gender:
        filtered_data = [user for user in data1 if user['gender'] == gender]
        # data1 = list(filter(lambda x: x['gender'] == gender, data1))
        my_logger.info('The data was filtered by gender')
    if num_rows and num_rows < len(data1):
        filtered_data = data1[:num_rows]
        my_logger.info('The data was filtered by num_rows')
    if not gender and (not num_rows or num_rows >= len(data1)):  # почему ту не работает else?
        my_logger.warning('The data was not filtered by any of the parameters!!!')
        return data1
    return filtered_data


def check_folder_existence(path):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)


def move_file_to_destination(initial_file_path, destination_folder):
    shutil.move(initial_file_path, destination_folder)


def rearrange_data(data1):
    new_structure = {}
    for data in data1:
        # decade = str(int(int(data['dob.date'][-2:]) / 10) * 10) + '-th'
        decade = str(int(int(data['dob.date'][-2:]) / 10)) + '0-th'
        country = data.pop('location.country')

        if decade not in new_structure:
            new_structure[decade] = {}

        if country not in new_structure[decade]:
            new_structure[decade][country] = []

        new_structure[decade][country].append(data)
    return new_structure


# def rearrange_data(data1):
#     return {
#         f"{str(int(data['dob.date'][-2:]) // 10 * 10)}-th": {
#             data.pop('location.country'): [data]
#             for data in data1
#         }
#     }


# def create_decade_subfolders(destination_folder, decades):
#     for decade in decades:  # for decade, data in decades.items():
#         subfolder_path = os.path.join(destination_folder, decade)
#         os.makedirs(subfolder_path, exist_ok=True)


def create_country_subfolders(destination_folder, data):
    for decade, countries in data.items():
        decade_folder = os.path.join(destination_folder, decade)
        os.makedirs(decade_folder, exist_ok=True)

        # for country in countries:
        #     country_folder = os.path.join(decade_folder, country)
        #     os.makedirs(country_folder, exist_ok=True)
        for country, country_data in countries.items():
            country_folder = os.path.join(decade_folder, country)
            os.makedirs(country_folder, exist_ok=True)
            max_age = max([data['dob.age'] for data in country_data])
            avg_registered = mean([int(data['registered.age']) for data in country_data])  # mean - avg
            most_common_id = Counter(([data['id.name'] for data in country_data])).most_common(1)[0][0]
            filename = os.path.join(country_folder, f'{max_age}_{avg_registered}_{most_common_id}.csv')
            # my_logger.info(f'Log paths {filename}.')
            write_data_in_csv(filename, country_data)


def remove_data_before_certain_decade(folder_path, decade):
    contents = os.listdir(folder_path)
    [shutil.rmtree(os.path.join(folder_path, f)) for f in contents if f[:2].isdigit() and int(f[:2]) < decade]
    # my_logger.info(f'Data brfore {decade} decade was removed!')


# def log_full_folder_structure(folder_path, logger, level=0):
    #     contents = os.listdir(folder_path)
    #     for item in contents:
    #         full_path = os.path.join(folder_path, item)
    #         if os.path.isfile(full_path):
    #             logger.info('\t' * level + f'[F] {item}')
    #         elif os.path.isdir(full_path):
    #             logger.info('\t' * level + f'[D] {item}')
    #             log_full_folder_structure(full_path, logger, level + 1)

def log_full_folder_structure(folder_path, logger, level=0):
    contents = os.listdir(folder_path)
    [logger.info('\t' * level + f'[F] {item}') if os.path.isfile(os.path.join(folder_path, item))
     else (logger.info('\t' * level + f'[D] {item}'),
           log_full_folder_structure(os.path.join(folder_path, item), logger, level + 1))
     for item in contents]


def create_zip_archive(output_zip_file, folder_path):
    shutil.make_archive(output_zip_file, 'zip', folder_path)


def main(output_folder, output_filename, log_lev, gender=None, num_rows=None):
    check_folder_existence(output_folder)
    # print("Current working directory:", os.getcwd()) E:\Programming\pythonProj\pythonProject\PythonCourse\Homework3
    my_logger = setup_logger(log_lev)

    download_user_accounts_csv('user_accounts_csv.csv', my_logger)
    print(f"Destination folder: {output_folder}")
    print(f"Filename: {output_filename}")
    print(f"Gender filter: {gender}")
    print(f"Number of rows filter: {num_rows}")
    print(f"Log level: {log_lev}")

    data = read_data_from_csv()  # 'user_accounts.csv'

    filtered_data = filter_data(data, my_logger, gender, num_rows)
    filtered_data = add_index_field(filtered_data)
    filtered_data = add_current_time(filtered_data)
    filtered_data = change_name_content(filtered_data)
    filtered_data = convert_to_format(filtered_data, 'dob.date', '%m-%d-%Y')  # dob.date
    filtered_data = convert_to_format(filtered_data, 'registered.date', '%m-%d-%Y, %H:%M:%S')  # register.date
    # pprint(filtered_data, indent=4)

    write_data_in_csv(os.path.join(output_folder, output_filename), filtered_data)

    test_data = [
        {'gender': 'male', 'dob.date': '1961', 'id.name': 'INSEE', 'location.country': 'USA'},
        {'gender': 'male', 'dob.date': '1964', 'id.name': 'IBDE', 'location.country': 'USA'},
        {'gender': 'female', 'dob.date': '1965', 'id.name': 'IBDQE', 'location.country': 'USA'}
    ]
    new_data = rearrange_data(filtered_data)
    # pprint(new_data, indent=4)

    # move_file_to_destination('user_accounts_csv.csv', output_folder)
    # create_decade_subfolders(output_folder, new_data)
    create_country_subfolders(output_folder, new_data)
    remove_data_before_certain_decade(output_folder, 60)
    log_full_folder_structure(output_folder, my_logger, level=0)
    # create_zip_archive('task_2', output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and filter user accounts data.')
    parser.add_argument('--output_folder', type=str,
                        help='Path to the destination folder where output file will be placed.')
    parser.add_argument('--output_filename', default='output.csv', type=str, help='Output filename (default: output)')
    # parser.add_mutually_exclusive_group()
    parser.add_argument('--gender', choices=['male', 'female'], type=str,
                        help='Filter data by gender (male or female).')
    parser.add_argument('--num_rows', type=int, help='Filter data by number of rows.')
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str, help='Log level (default: INFO).')

    args = parser.parse_args()
    log_level = getattr(logging, args.log_level.upper())

    main(args.output_folder, args.output_filename, log_level, args.gender, args.num_rows)


