import os
import logging
import csv
import requests
import argparse
import shutil
from datetime import datetime, timedelta
from statistics import mean
from collections import Counter

URL = 'https://randomuser.me/api/?results=5000&format=csv'


def setup_logger():
    logging.basicConfig(
        filename='my_log_file.log',
        level=logging.DEBUG,  #
        format='%(asctime)s - %(levelname)s - %(message)s"'
    )
    return logging.getLogger('my_logger')


my_logger = setup_logger()


def download_user_accounts_csv(output_csv):
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
    with open('user_accounts.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def write_data_in_csv(file_path, data1):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(data1[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data1)
        my_logger.info(f'Data was written in {file_path}.')


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
    my_logger.info(f'Add current time field')
    return data1


def change_name_content(data1):
    rule_list = {'Mrs': 'missis', 'Ms ': 'miss', 'Mr': 'mister', 'Madame': 'mademoiselle'}
    for data in data1:
        if data['name.title'] in rule_list:
            data['name.title'] = rule_list[data['name.title']]
    my_logger.info(f'The content was changed in the field "name.title"')
    return data1


def convert_to_format(data1, field='dob.date', format_string='%Y-%m-%d'):
    for data in data1:
        dob = datetime.strptime(data[field], '%Y-%m-%dT%H:%M:%S.%fZ')
        data[field] = dob.strftime(format_string)
    my_logger.info(f'Format of field {field} was changed to {format_string}')
    return data1


def filter_data(data1, gender=None, num_rows=None):
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
        my_logger.info(f'The folder was created along the path {path} ')
    os.chdir(path)


def move_file_to_destination(initial_file_path, destination_folder):
    shutil.move(initial_file_path, destination_folder)
    my_logger.info(f'The {initial_file_path} was moved to {destination_folder} ')


def rearrange_data(data1):
    new_structure = {}
    for data in data1:
        decade = str(int(int(data['dob.date'][-2:]) / 10)) + '0-th'
        country = data.pop('location.country')

        if decade not in new_structure:
            new_structure[decade] = {}

        if country not in new_structure[decade]:
            new_structure[decade][country] = []

        new_structure[decade][country].append(data)
    my_logger.info('The data was rearranged')
    return new_structure


def create_subfolders(destination_folder, data):
    for decade, countries in data.items():
        decade_folder = os.path.join(destination_folder, decade)
        os.makedirs(decade_folder, exist_ok=True)

        for country, country_data in countries.items():
            country_folder = os.path.join(decade_folder, country)
            os.makedirs(country_folder, exist_ok=True)
            max_age = max([data['dob.age'] for data in country_data])
            avg_registered = round(mean([int(data['registered.age']) for data in country_data]), 1)  # mean - avg
            most_common_id = Counter(([data['id.name'] for data in country_data])).most_common(1)[0][0]
            filename = os.path.join(country_folder, f'{max_age}_{avg_registered}_{most_common_id}.csv')
            my_logger.info(f'Log paths {filename} was created.')
            write_data_in_csv(filename, country_data)


def remove_data_before_certain_decade(folder_path, decade):
    contents = os.listdir(folder_path)
    [shutil.rmtree(os.path.join(folder_path, f)) for f in contents if f[:2].isdigit() and int(f[:2]) < decade]
    my_logger.info(f'Data before {decade} decade was removed!')


def log_full_folder_structure(folder_path, level=0):
    contents = os.listdir(folder_path)
    [my_logger.info('\t' * level + f'[F] {item}') if os.path.isfile(os.path.join(folder_path, item))
     else (my_logger.info('\t' * level + f'[D] {item}'),
           log_full_folder_structure(os.path.join(folder_path, item), level + 1))
     for item in contents]


def create_zip_archive(output_zip_file, folder_path):
    os.chdir('..')
    shutil.make_archive(output_zip_file, 'zip', folder_path)
    my_logger.info(f'Zip archive {output_zip_file} was created!')


def preprocess_data(data, gender, num_rows):
    filtered_data = filter_data(data, gender, num_rows)
    filtered_data = add_index_field(filtered_data)
    filtered_data = add_current_time(filtered_data)
    filtered_data = change_name_content(filtered_data)
    filtered_data = convert_to_format(filtered_data, 'dob.date', '%m-%d-%Y')
    filtered_data = convert_to_format(filtered_data, 'registered.date', '%m-%d-%Y, %H:%M:%S')
    my_logger.info('Data was filtered!')
    return filtered_data


def main(output_folder, output_filename, log_lev, gender=None, num_rows=None):
    check_folder_existence(output_folder)
    my_logger.setLevel(log_lev)

    download_user_accounts_csv('user_accounts.csv')
    print(f"Destination folder: {output_folder}")
    print(f"Filename: {output_filename}")
    print(f"Gender filter: {gender}")
    print(f"Number of rows filter: {num_rows}")
    print(f"Log level: {log_lev}")

    data = read_data_from_csv()

    filtered_data = preprocess_data(data, gender, num_rows)

    write_data_in_csv(os.path.join(output_folder, output_filename), filtered_data)
    new_data = rearrange_data(filtered_data)
    # move_file_to_destination('user_accounts_csv.csv', output_folder)
    create_subfolders(output_folder, new_data)
    remove_data_before_certain_decade(output_folder, 60)
    log_full_folder_structure(output_folder, level=0)
    create_zip_archive('task_2', output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and filter user accounts data.')
    parser.add_argument('--output_folder', type=str,
                        help='Path to the destination folder where output file will be placed.')
    parser.add_argument('--output_filename', default='output.csv', type=str, help='Output filename (default: output)')
    # parser.add_mutually_exclusive_group()  ? should i use it here? for --gender and --num_rows
    parser.add_argument('--gender', choices=['male', 'female'], type=str,
                        help='Filter data by gender (male or female).')
    parser.add_argument('--num_rows', type=int, help='Filter data by number of rows.')
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str, help='Log level (default: INFO).')

    args = parser.parse_args()
    log_level = getattr(logging, args.log_level.upper())

    main(args.output_folder, args.output_filename, log_level, args.gender, args.num_rows)
