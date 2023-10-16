import unittest
from unittest.mock import patch
from movie_lab import MovieDataGrabber
from var4 import sum_diagonal_parallel
from task_2 import add_current_time, rearrange_data, change_name_content
from datetime import datetime, timedelta

TEST_MATRIX_1 = [[6, 11, 174, 156], [26, -38, 92, -43], [104, 69, 69, -43], [105, 161, 100, 136]]


def test_delete_movie_by_genre():
    movie_data_grabber = MovieDataGrabber()

    movie_data_grabber.genres_data = [{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'},
                                      {'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'},
                                      {'id': 80, 'name': 'Crime'}]
    movie_data_grabber.data = [
        {'title': 'Movie 2', 'genre_ids': [28, 12, 80]},
        {'title': 'Movie 3', 'genre_ids': [80, 16]},
    ]
    movie_data_grabber.delete_movie_by_genre('Action')
    expected_data = [
        {'title': 'Movie 3', 'genre_ids': [80, 16]}
    ]
    assert movie_data_grabber.data == expected_data


test_data = [
    {'gender': 'male', 'dob.date': '1961', 'id.name': 'INSEE', 'location.country': 'USA'},
    {'gender': 'male', 'dob.date': '1964', 'id.name': 'IBDE', 'location.country': 'USA'},
    {'gender': 'female', 'dob.date': '1955', 'id.name': 'IBDQE', 'location.country': 'USA'}
]


def test_rearrange_data():
    expected_result = {
        '50-th': {
            'USA': [
                {'gender': 'female', 'dob.date': '1955', 'id.name': 'IBDQE'}
            ]
        },
        '60-th': {
            'USA': [
                {'gender': 'male', 'dob.date': '1961', 'id.name': 'INSEE'},
                {'gender': 'male', 'dob.date': '1964', 'id.name': 'IBDE'}
            ]
        }
    }
    result = rearrange_data(test_data)
    assert result == expected_result


def test_sum_diagonal_parallel():
    input_param1 = TEST_MATRIX_1
    input_param2 = 4
    actual = sum_diagonal_parallel(input_param1, input_param2)
    expected = [105, 265, 195, 156, 131, 60]
    assert actual == expected


@patch.object(MovieDataGrabber, 'calculate_last_day_in_cinema')
def test_transform_movie_data(mock_calculate_last_day_in_cinema):
    grabber = MovieDataGrabber()
    grabber.data = {'adult': False, 'backdrop_path': '/iIvQnZyzgx9TkbrOgcXx0p7aLiq.jpg', 'genre_ids': [27, 53],
                    'id': 1008042,
                    'original_language': 'en', 'original_title': 'Talk to Me',
                    'overview': 'When a group of friends discover how to conjure spirits using an embalmed hand, they become hooked on the new thrill, until one of them goes too far and unleashes terrifying supernatural forces.',
                    'popularity': 2216.018, 'poster_path': '/kdPMUMJzyYAc4roD52qavX0nLIC.jpg',
                    'release_date': '2023-07-26',
                    'title': 'Talk to Me', 'video': False, 'vote_average': 7.3, 'vote_count': 1307}

    mock_calculate_last_day_in_cinema.return_value = '2023-10-04'

    expected = {'title': 'Talk to Me', 'popularity': 2216.0, 'score': 7, 'last_day_in_cinema': '2023-10-04'}
    actual = grabber.transform_movie_data(grabber.data)

    assert expected == actual


class TestFindFileNameComponents(unittest.TestCase):
    def setUp(self):
        self.test_data = {'cell': '061-4189-159',
                          'dob.age': '61',
                          'dob.date': '1961-10-17T20:34:48.044Z',
                          'email': 'damir.serbedzija@example.com',
                          'gender': 'male',
                          'id.name': 'SID',
                          'id.value': '367099576',
                          'location.city': 'Brus',
                          'location.coordinates.latitude': '-58.3012',
                          'location.coordinates.longitude': '-129.7441',
                          'location.country': 'Serbia',
                          'location.postcode': '29663',
                          'location.state': 'Peć',
                          'location.street.name': 'Petra Nikšića',
                          'location.street.number': '2255',
                          'location.timezone.description': 'Midway Island, Samoa',
                          'location.timezone.offset': '-11:00',
                          'login.md5': '655f238ffb125e4eb2c54e4a6d03bbad',
                          'login.password': '545454',
                          'login.salt': 'ItW3Ryhl',
                          'login.sha1': 'c4d2d03e3eaf6d9f55c0321f36ac8f0ce493e7b0',
                          'login.sha256': '2e86448645061c92a77648fdeb71deeb66d81001a5bc74efae149ef4d994ef2e',
                          'login.username': 'ticklishostrich867',
                          'login.uuid': '759d7085-258a-499f-9026-f8b31f741a20',
                          'name.first': 'Damir',
                          'name.last': 'Šerbedžija',
                          'name.title': 'Mr',
                          'nat': 'RS',
                          'phone': '025-5594-243',
                          'picture.large': 'https://randomuser.me/api/portraits/men/93.jpg',
                          'picture.medium': 'https://randomuser.me/api/portraits/med/men/93.jpg',
                          'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/93.jpg',
                          'registered.age': '15',
                          'registered.date': '2008-07-12T12:54:48.709Z'}

    @patch('datetime.datetime')
    def test_add_current_time(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 10, 14, 5, 12, 52)
        actual = add_current_time(self.test_data)
        expected = {'cell': '061-4189-159',
                    'current_time': '2023-10-14 05:18:29',
                    'dob.age': '61',
                    'dob.date': '1961-10-17T20:34:48.044Z',
                    'email': 'damir.serbedzija@example.com',
                    'gender': 'male',
                    'id.name': 'SID',
                    'id.value': '367099576',
                    'location.city': 'Brus',
                    'location.coordinates.latitude': '-58.3012',
                    'location.coordinates.longitude': '-129.7441',
                    'location.country': 'Serbia',
                    'location.postcode': '29663',
                    'location.state': 'Peć',
                    'location.street.name': 'Petra Nikšića',
                    'location.street.number': '2255',
                    'location.timezone.description': 'Midway Island, Samoa',
                    'location.timezone.offset': '-11:00',
                    'login.md5': '655f238ffb125e4eb2c54e4a6d03bbad',
                    'login.password': '545454',
                    'login.salt': 'ItW3Ryhl',
                    'login.sha1': 'c4d2d03e3eaf6d9f55c0321f36ac8f0ce493e7b0',
                    'login.sha256': '2e86448645061c92a77648fdeb71deeb66d81001a5bc74efae149ef4d994ef2e',
                    'login.username': 'ticklishostrich867',
                    'login.uuid': '759d7085-258a-499f-9026-f8b31f741a20',
                    'name.first': 'Damir',
                    'name.last': 'Šerbedžija',
                    'name.title': 'Mr',
                    'nat': 'RS',
                    'phone': '025-5594-243',
                    'picture.large': 'https://randomuser.me/api/portraits/men/93.jpg',
                    'picture.medium': 'https://randomuser.me/api/portraits/med/men/93.jpg',
                    'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/93.jpg',
                    'registered.age': '15',
                    'registered.date': '2008-07-12T12:54:48.709Z'}
        assert actual == expected

    def test_change_name_content(self):
        actual = change_name_content(self.test_data)
        print(actual)
        expected = {'cell': '061-4189-159',
                    'dob.age': '61',
                    'dob.date': '1961-10-17T20:34:48.044Z',
                    'email': 'damir.serbedzija@example.com',
                    'gender': 'male',
                    'id.name': 'SID',
                    'id.value': '367099576',
                    'location.city': 'Brus',
                    'location.coordinates.latitude': '-58.3012',
                    'location.coordinates.longitude': '-129.7441',
                    'location.country': 'Serbia',
                    'location.postcode': '29663',
                    'location.state': 'Peć',
                    'location.street.name': 'Petra Nikšića',
                    'location.street.number': '2255',
                    'location.timezone.description': 'Midway Island, Samoa',
                    'location.timezone.offset': '-11:00',
                    'login.md5': '655f238ffb125e4eb2c54e4a6d03bbad',
                    'login.password': '545454',
                    'login.salt': 'ItW3Ryhl',
                    'login.sha1': 'c4d2d03e3eaf6d9f55c0321f36ac8f0ce493e7b0',
                    'login.sha256': '2e86448645061c92a77648fdeb71deeb66d81001a5bc74efae149ef4d994ef2e',
                    'login.username': 'ticklishostrich867',
                    'login.uuid': '759d7085-258a-499f-9026-f8b31f741a20',
                    'name.first': 'Damir',
                    'name.last': 'Šerbedžija',
                    'name.title': 'mister',
                    'nat': 'RS',
                    'phone': '025-5594-243',
                    'picture.large': 'https://randomuser.me/api/portraits/men/93.jpg',
                    'picture.medium': 'https://randomuser.me/api/portraits/med/men/93.jpg',
                    'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/93.jpg',
                    'registered.age': '15',
                    'registered.date': '2008-07-12T12:54:48.709Z'}
        assert actual == expected
