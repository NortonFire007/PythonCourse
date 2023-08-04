import os
import logging
import csv
import requests
import argparse

URL = 'https://randomuser.me/api/?results=5000'


def setup_logger(log_file, log_level=logging.DEBUG):
    logger = logging.getLogger("my_logger")
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def download_user_accounts_csv(url, my_logger):
    my_logger.info("Downloading user accounts data from the API...")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('results', [])
        if data:
            my_logger.info(f"Received {len(data)} user accounts from the API.")
            with open('user_accounts.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            my_logger.info("Successfully downloaded user accounts to 'user_accounts.csv'")
        else:
            my_logger.warning("No data received from the API.")
    else:
        my_logger.error(f"Failed to fetch data. Status code: {response.status_code}")

    def filter_data(data1, gender=None, num_rows=None):
        if gender:
            data1 = [user for user in data1 if user['gender'] == gender]
        if num_rows and num_rows < len(data1):
            data1 = data1[:num_rows]
        return data1


def main(output_folder, output_filename, log_lev, gender=None, num_rows=None):
    my_logger = setup_logger('my_log_file.log', log_lev)
    download_user_accounts_csv(URL, my_logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download and filter user accounts data.')
    parser.add_argument('--output_folder', help='Path to the destination folder where output file will be placed.')
    parser.add_argument('--output_filename', default='output', help='Output filename (default: output)')
    parser.add_argument('--gender', choices=['male', 'female'], help='Filter data by gender (male or female).')
    parser.add_argument('--num_rows', type=int, help='Filter data by number of rows.')
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        help='Log level (default: INFO).')

    args = parser.parse_args()
    log_level = getattr(logging, args.log_level)

    main(args.output_folder, args.output_filename, log_level, args.gender, args.num_rows)
