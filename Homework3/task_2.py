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
        level=logging.DEBUG,
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
            my_logger.info('Received user accounts from the API.')
            with open(output_csv, 'w', encoding='utf-8') as file:
                file.write(data)
            my_logger.info(f'Successfully downloaded user accounts to {output_csv}')
        else:
            my_logger.warning('No data received from the API.')
    else:
        my_logger.error(f'Failed to fetch data. Status code: {response.status_code}')


def read_data_from_csv():
    with open('user_accounts.csv', 'r', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))


def write_data_in_csv(file_path, input_data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(input_data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(input_data)
        my_logger.info(f'Data was written in {file_path}.')


def add_index_field(input_data):
    for index, data in enumerate(input_data, start=1):
        data['global_index'] = index
    return input_data


def add_timezone_offset(datetime_str, offset_str):
    hours, minutes = map(int, offset_str.split(':'))
    offset = timedelta(hours=hours, minutes=minutes)

    dt_with_offset = datetime_str + offset
    return dt_with_offset.strftime('%Y-%m-%d %H:%M:%S')


def add_current_time(input_data):
    for data in input_data:
        timezone_offset = data['location.timezone.offset']
        current_time = datetime.now()
        data['current_time'] = add_timezone_offset(current_time, timezone_offset)
    my_logger.info(f'Add current time field')
    return input_data


def change_name_content(input_data):
    rule_list = {'Mrs': 'missis', 'Ms ': 'miss', 'Mr': 'mister', 'Madame': 'mademoiselle'}
    my_logger.info('The content was changed in the field "name.title"')
    return [{'name.title': rule_list.get(data['name.title'], data['name.title']), **data} for data in input_data]


def convert_to_format(input_data, field='dob.date', format_string='%Y-%m-%d'):
    for data in input_data:
        dob = datetime.strptime(data[field], '%Y-%m-%dT%H:%M:%S.%fZ')
        data[field] = dob.strftime(format_string)
    my_logger.info(f'Format of field {field} was changed to {format_string}')
    return input_data


def filter_data(input_data, gender=None, num_rows=None):
    if gender:
        filtered_data = [user for user in input_data if user['gender'] == gender]
        # input_data = list(filter(lambda x: x['gender'] == gender, input_data))
        my_logger.info('The data was filtered by gender')
    elif num_rows and num_rows < len(input_data):
        filtered_data = input_data[:num_rows]
        my_logger.info('The data was filtered by num_rows')
    else:
        my_logger.warning('The data was not filtered by any of the parameters!!!')
        return input_data
    return filtered_data


def check_folder_existence(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        my_logger.info(f'The folder was created along the path {path} ')
    os.chdir(path)


def move_file_to_destination(initial_file_path, destination_folder):
    shutil.move(initial_file_path, destination_folder)
    my_logger.info(f'The {initial_file_path} was moved to {destination_folder} ')


def rearrange_data(input_data):
    new_structure = {}
    for data in input_data:
        decade = f"{data['dob.date'][-2]}0-th"
        country = data.pop('location.country')

        new_structure.setdefault(decade, {}).setdefault(country, []).append(data)

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
            avg_registered = round(mean([int(data['registered.age']) for data in country_data]), 1)
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


def create_parser():
    parser = argparse.ArgumentParser(description='Download and filter user accounts data.')
    parser.add_argument('--output_folder', type=str, required=True,
                        help='Path to the destination folder where output file will be placed.')
    parser.add_argument('--output_filename', default='output.csv', type=str, help='Output filename (default: output)')
    parser.add_argument('--gender', choices=['male', 'female'], type=str,
                        help='Filter data by gender (male or female).')
    parser.add_argument('--num_rows', type=int, help='Filter data by number of rows.')
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        type=str, help='Log level (default: INFO).')
    return parser


def main(output_folder, output_filename, log_lev, gender=None, num_rows=None):
    check_folder_existence(output_folder)
    my_logger.setLevel(log_lev)

    download_user_accounts_csv('user_accounts.csv')

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
    my_parser = create_parser()
    args = my_parser.parse_args()
    log_level = getattr(logging, args.log_level.upper())

    main(args.output_folder, args.output_filename, log_level, args.gender, args.num_rows)
