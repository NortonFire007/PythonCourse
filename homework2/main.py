import requests
from collections import Counter
from datetime import datetime, timedelta
import csv

FIELD_NAMES = ['title', 'popularity', 'score', 'last_day_in_cinema']
API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'


class MovieDataGrabber:
    def __init__(self, num_pages=1):
        self.api_key = API_KEY
        self.num_pages = num_pages
        self.url = 'https://api.themoviedb.org/3/'
        self.data = []
        self.genres_data = None
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        self.params = {
            'include_adult': False,
            'include_video': False,
            'sort_by': 'popularity.desc'
        }
        self.fetch_data()
        self.fetch_genres_data()

    def fetch_data(self):
        for page_num in range(1, self.num_pages + 1):
            self.params['page'] = page_num
            response = requests.get(f'{self.url}discover/movie', params=self.params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.data.extend(data.get('results', []))
            else:
                print(f'Error fetching data from page {page_num}')

    def fetch_genres_data(self):
        try:
            response = requests.get(f'{self.url}genre/movie/list?language=en', headers=self.headers)
            response.raise_for_status()

            genres_data = response.json()
            self.genres_data = genres_data.get('genres', [])

        except requests.exceptions.RequestException as e:
            print(f'Error fetching genres data: {e}')

    def get_all_data(self):
        return self.data

    def get_genres_data(self):
        return self.genres_data

    def get_data_by_indexes(self, start_index, end_index, step):
        return self.data[start_index:end_index:step]

    def get_most_popular_title(self):
        return max(self.data, key=lambda x: x['popularity']).get('title', '')

    def get_titles_by_description_key_words(self, keywords):
        return [movie.get('title', '') for movie in self.data if
                any(keyword in movie.get('overview', '').lower() for keyword in keywords.lower().split())]

    def get_unique_genres(self):
        return (genre['name'] for genre in self.genres_data)

    def delete_movie_by_genre(self, genre):
        # genre_id = (item['id'] for item in self.genres_data if item['name'] == genre)[0]
        genre_id = [item['id'] for item in self.genres_data if item['name'] == genre].pop()
        self.data = [movie for movie in self.data if genre_id not in movie.get('genre_ids', [])]

    def names_of_most_popular_genres(self, count=1):
        all_genre_ids = [genre_id for movie in self.data for genre_id in movie.get('genre_ids', [])]
        most_common_genre_ids = Counter(all_genre_ids).most_common(count)
        genre_id_to_name = {item['id']: item['name'] for item in self.genres_data}
        return [(genre_id_to_name[id_val], score_val)
                for id_val, score_val in most_common_genre_ids]

    def group_titles_in_pairs_by_common_genres(self):
        return [(movie1['title'], movie2['title'])
                for i, movie1 in enumerate(self.data)
                for movie2 in self.data[i + 1:]
                if any(genre in movie2['genre_ids'] for genre in movie1['genre_ids'])]

    def get_initial_and_copy_data(self):
        return self.data, [{**movie, 'genre_ids': [22, *movie['genre_ids'][1:]]} for movie in self.data]

    @staticmethod
    def calculate_last_day_in_cinema(date):
        return (datetime.strptime(date, '%Y-%m-%d') + timedelta(weeks=10)).strftime('%Y-%m-%d')

    def transform_movie_data(self, movie):
        return {
            'title': movie.get('title', ''),
            'popularity': round(movie.get('popularity', 0), 1),
            'score': int(movie.get('vote_average', 0)),
            'last_day_in_cinema': self.calculate_last_day_in_cinema(movie.get('release_date', ''))
        }

    def make_collections_with_structure(self):
        return sorted(map(self.transform_movie_data, self.data), key=lambda x: (x['popularity'], x['score']),
                      reverse=True)

    @staticmethod
    def write_to_csv(movie_data, file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(movie_data)


def main():
    print('Task 1: make movie_grabber\n')
    movie_grabber = MovieDataGrabber(num_pages=3)

    data_from_pages = movie_grabber.get_all_data()
    print(f'Task 2:\nData from desired pages: \n{data_from_pages}')

    genres_data = movie_grabber.get_genres_data()
    print(f'Genres data: \n {genres_data}')

    data_by_indexes = movie_grabber.get_data_by_indexes(3, 19, 4)
    print(f'\nTask 3:\nData with indexes from 3 to 19 with step 4:\n {data_by_indexes}')

    most_popular_title = movie_grabber.get_most_popular_title()
    print(f'\nTask 4:\nMost popular  title: {most_popular_title}')

    description = 'barbie human'

    titles_by_description_key_words = movie_grabber.get_titles_by_description_key_words(description)
    if titles_by_description_key_words:
        print(f'\nTask 5:\nTitles by description "{description}": ')
        for i in titles_by_description_key_words:
            print(i)
    else:
        print(f'\nBy description "{description}" no matches found :( ')

    unique_present_genres = movie_grabber.get_unique_genres()
    print('\nTask 6:\nSet of present genres": ')
    for i in unique_present_genres:
        print(i)

    movie_grabber.delete_movie_by_genre('Action')
    data_from_pages = movie_grabber.get_all_data()
    print(f'\nTask 7:\nMovies data after removing genre "Action":\n {data_from_pages} ')

    most_popular_genres = movie_grabber.names_of_most_popular_genres(count=5)
    print(f'\nTask 8:\nMost popular genres:')
    for genre, occurrences in most_popular_genres:
        print('f"{genre} genre occurs {occurrences} times"')

    titles_in_pairs = movie_grabber.group_titles_in_pairs_by_common_genres()
    print(f'\nTask 9:\nCollection of film titles grouped in pairs by common genres:\n {titles_in_pairs}')

    print(f'\nTask 10:\n{movie_grabber.get_initial_and_copy_data()[0]}\n{movie_grabber.get_initial_and_copy_data()[1]}')

    print(f'\nTask 11:')
    collections_with_structure = movie_grabber.make_collections_with_structure()
    for i in collections_with_structure:
        print(i)

    path = 'films.csv'
    print(f'\nTask 12: Write information to a csv file by path {path}')
    movie_grabber.write_to_csv(collections_with_structure, path)


if __name__ == '__main__':
    main()
