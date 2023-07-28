import requests


# headers = {
#     "accept": "application/json",
#     "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
# }
#
# url = "https://api.themoviedb.org/3/discover/movie"
#
# params = {
#     'include_adult': False,
#     'include_video': False,
#     'sort_by': 'popularity.desc'
# }

# response = requests.get(url, params=params, headers=headers)
# print(response.json())


class MovieDataGrabber:
    def __init__(self, api_key, num_pages=1):
        self.api_key = api_key
        self.num_pages = num_pages
        self.url = "https://api.themoviedb.org/3/discover/movie"

        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.params = {
            'include_adult': False,
            'include_video': False,
            'sort_by': 'popularity.desc'
        }

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

        return all_data

    def get_all_data(self):
        return self.fetch_data()

    def get_data_by_indexes(self, start_index, end_index, step):
        all_data = self.fetch_data()
        return all_data[start_index:end_index:step]

    # def get_most_popular_title(self):  #для одного популярного фильма
    #     all_data = self.fetch_data()
    #     if all_data:
    #         most_popular_movie = max(all_data, key=lambda x: x['popularity'])
    #         return most_popular_movie.get('title', '')
    #     return ""
    def get_most_popular_title(self, count):  # для нескольких популярных фильмов
        all_data = self.fetch_data()
        if all_data:

            popular_titles = []

            for i in range(count):
                most_popular_movie = max(all_data, key=lambda x: x['popularity'])
                popular_titles.append(most_popular_movie.get('title', ''))
                all_data.remove(most_popular_movie)  # Удаляем найденный фильм из списка данных, чтобы не повторять его

            return popular_titles

        return 'Empty data list'

    def get_titles_by_description_key_words(self, keywords):
        all_data = self.fetch_data()
        if all_data and keywords:
            keywords = keywords.split()

            def has_keyword(movie):
                return any(keyword.lower() in movie.get('overview', '').lower() for keyword in keywords)

            titles_with_keywords = filter(has_keyword, all_data)

            titles = [movie.get('title', '') for movie in titles_with_keywords]

            return titles

        return 'Error: Either all_data or keywords (or both) are empty.'


def main():
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"

    movie_grabber = MovieDataGrabber(api_key, num_pages=1)

    data_from_pages = movie_grabber.get_all_data()
    print("Data from desired pages:")
    print(data_from_pages)

    data_by_indexes = movie_grabber.get_data_by_indexes(3, 19, 4)
    print("\nData with indexes from 3 to 19 with step 4:")
    print(data_by_indexes)

    most_popular_title = movie_grabber.get_most_popular_title(3)
    print("\nMost popular 3 titles:")
    for i in most_popular_title:
        print(i)

    description = 'tennis'  #no matches found
    description = 'human barbie'  #['Barbie', 'Transformers: Rise of the Beasts', 'The Little Mermaid' ...]
    # description = ['human', 'barbie', 'tennis']

    titles_by_description_key_words = movie_grabber.get_titles_by_description_key_words(description)
    if titles_by_description_key_words:
        print(f'\nTitles by description "{description}": ')
        # print(titles_by_description_key_words)
        for i in titles_by_description_key_words:
            print(i)

    else:
        print(f'\nBy description "{description}" no matches found :( ')


main()
