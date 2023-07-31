import requests
from collections import Counter
from datetime import datetime, timedelta
import csv
import copy


class MovieDataGrabber:
    def __init__(self, api_key, num_pages=1):
        self.api_key = api_key
        self.num_pages = num_pages
        self.url = "https://api.themoviedb.org/3/discover/movie"
        self.data = None
        self.genres_data = None
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.params = {
            'include_adult': False,
            'include_video': False,
            'sort_by': 'popularity.desc'
        }
        self.fetch_data()
        self.fetch_genres_data()

    def fetch_data(self):
        all_data = []
        for page_num in range(1, self.num_pages + 1):
            self.params['page'] = page_num
            response = requests.get(self.url, params=self.params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                all_data.extend(data.get('results', []))
            else:
                print(f"Error fetching data from page {page_num}")

        self.data = all_data

    def fetch_genres_data(self):
        try:
            response = requests.get("https://api.themoviedb.org/3/genre/movie/list?language=en", headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad responses (e.g., 404, 500)

            genres_data = response.json()
            genres_data.get('genres', [])
            self.genres_data = genres_data
            # return genres_data.get('genres', [])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching genres data: {e}")
            # return []

    def get_all_data(self):
        return self.data

    def get_genres_data(self):
        return self.genres_data

    def get_data_by_indexes(self, start_index, end_index, step):
        return self.data[start_index:end_index:step]

    # def get_most_popular_title(self):  #для одного популярного фильма
    #     all_data = self.fetch_data()
    #     return max(all_data, key=lambda x: x['popularity']).get('title', '') if all_data else ""
    def get_most_popular_title(self, count):  # для нескольких популярных фильмов
        all_data = self.data.copy()
        if all_data:
            popular_titles = []

            for i in range(count):
                most_popular_movie = max(all_data, key=lambda x: x['popularity'])
                popular_titles.append(most_popular_movie.get('title', ''))
                all_data.remove(most_popular_movie)  # Удаляем найденный фильм из списка данных, чтобы не повторять его

            return popular_titles

        return 'Empty data list'

    def get_titles_by_description_key_words(self, keywords):
        if self.data and keywords:
            keywords = keywords.lower().split()
            return [movie.get('title', '') for movie in self.data if
                    any(keyword in movie.get('overview', '').lower() for keyword in keywords)]
            # keywords = keywords.split()
            # def has_keyword(movie):
            #     return any(keyword.lower() in movie.get('overview', '').lower() for keyword in keywords)
            #
            # titles_with_keywords = filter(has_keyword, self.data)
            #
            # titles = [movie.get('title', '') for movie in titles_with_keywords]
            #
            # return titles

        return 'Not found'

    def get_unique_genres(self):
        return [genre['name'] for genre in self.genres_data['genres']]

    def get_genre_id_by_name(self, genre_name):
        for genre in self.genres_data.get('genres', []):
            if genre['name'] == genre_name:
                return genre['id']
        return None

    def get_genre_name_by_id(self, genre_id):
        for genre in self.genres_data.get('genres', []):
            if genre['id'] == genre_id:
                return genre['name']
        return None

    def delete_movie_by_genre(self, genre):
        genre_id = self.get_genre_id_by_name(genre)
        genre_ids_to_delete = {movie['id'] for movie in self.data if genre_id in movie.get('genre_ids', [])}
        self.data = [movie for movie in self.data if movie['id'] not in genre_ids_to_delete]
        # genre_id = self.get_genre_id_by_name(genre)
        # genre_ids_to_delete = set()
        # for movie in self.data:
        #     if genre_id in movie.get('genre_ids', []):
        #         genre_ids_to_delete.add(movie['id'])
        #
        # self.data = [movie for movie in self.data if movie['id'] not in genre_ids_to_delete]

    def names_of_most_popular_genres(self, count=1):
        all_genre_ids = [genre_id for movie in self.data for genre_id in movie.get('genre_ids', [])]

        genre_id_counts = Counter(all_genre_ids)

        most_common_genre_ids = genre_id_counts.most_common(count)

        most_common_genre_names = [genre['name'] for genre_id, _ in most_common_genre_ids
                                   for genre in self.genres_data['genres'] if genre['id'] == genre_id]

        return most_common_genre_names

    @staticmethod
    def make_copy(data):
        return copy.deepcopy(data)

    def get_initial_and_copy_data(self):
        copied_data = self.make_copy(self.data)
        return self.data, [
            {**movie, 'genre_ids': [22, *movie['genre_ids'][1:]]}
            if 'genre_ids' in movie and movie['genre_ids']
            else movie
            for movie in copied_data
        ]

    @staticmethod
    def calculate_last_day_in_cinema(date):
        date = datetime.strptime(date, "%Y-%m-%d")
        last_day = date + timedelta(weeks=10)
        return last_day.strftime("%Y-%m-%d")

    def make_collections_with_structure(self):
        collections_with_structure = []
        sorted_data = []

        for movie in self.data:
            title = movie.get('title', '')
            popularity = round(movie.get('popularity', 0), 1)
            score = int(movie.get('vote_average', 0))
            release_date = movie.get('release_date', '')
            last_day_in_cinema = self.calculate_last_day_in_cinema(release_date)

            collections_with_structure.append({
                'title': title,
                'popularity': popularity,
                'score': score,
                'last_day_in_cinema': last_day_in_cinema
            })

            sorted_data = sorted(collections_with_structure, key=lambda x: (x['popularity'], x['score']), reverse=True)
        return sorted_data

    @staticmethod
    def write_to_csv(movie_data, file_path):
        field_names = ['title', 'popularity', 'score', 'last_day_in_cinema']

        with open(file_path, mode='w') as csv_file:
            # writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer = csv.writer(csv_file)
            writer.writerow(field_names)
            # writer.writeheader()
            for movie in movie_data:
                row_values = [movie[field] for field in field_names]
                writer.writerow(row_values)


def main():
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"

    print('Task 1: make movie_grabber\n')
    movie_grabber = MovieDataGrabber(api_key, num_pages=3)

    data_from_pages = movie_grabber.get_all_data()
    print(f'Task 2:\nData from desired pages: \n{data_from_pages}')

    genres_data = movie_grabber.get_genres_data()
    print(f'Genres data: \n {genres_data}')

    data_by_indexes = movie_grabber.get_data_by_indexes(3, 19, 4)
    print(f'\nTask 3:\nData with indexes from 3 to 19 with step 4:\n {data_by_indexes}')

    most_popular_title = movie_grabber.get_most_popular_title(3)
    print('\nTask 4:\nMost popular 3 titles:')
    for i in most_popular_title:
        print(i)

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
    print(data_from_pages)

    most_popular_genres = movie_grabber.names_of_most_popular_genres(count=3)
    print(f'\nTask 8:\nMost popular genres:\n {most_popular_genres}')

    print(f'\nTask 10:{movie_grabber.get_initial_and_copy_data()[0]}\n{movie_grabber.get_initial_and_copy_data()[1]}')

    print(f'\nTask 11:')
    collections_with_structure = movie_grabber.make_collections_with_structure()
    for i in collections_with_structure:
        print(i)

    path = 'films.csv'
    print(f'\nTask 12: Write information to a csv file by path {path}')
    movie_grabber.write_to_csv(collections_with_structure, path)


if __name__ == '__main__':
    main()
