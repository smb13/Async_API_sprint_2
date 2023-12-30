import copy
import random
import uuid

from faker import Faker
from functools import reduce


fake = Faker()

# Умноженное на 2 значение должно быть больше page_size
ES_MOVIES_A_HALF_OF_TEST_RECORDS = 30
ES_MOVIES_NUMBER_OF_TEST_RECORDS = ES_MOVIES_A_HALF_OF_TEST_RECORDS * 2

ES_MOVIES_TEST_DATA = [{
    'uuid': str(uuid.uuid4()),
    'imdb_rating': 8.5,
    'genre': [
        {'uuid': '2394b4d4-a0f1-11ee-8c90-0242ac120002', 'name': 'Action'},
        {'uuid': '420be6f8-a0f1-11ee-8c90-0242ac120002', 'name': 'Sci-Fi'}
    ],
    'title': 'The Star',
    'description': 'New World',
    'directors': [
        {'uuid': 'b3cc5f9e-a0f0-11ee-8c90-0242ac120002', 'full_name': 'Stan'}
    ],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'actors': [
        {'uuid': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
        {'uuid': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
    ],
    'writers': [
        {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
        {'uuid': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
    ],
} for _ in range(ES_MOVIES_A_HALF_OF_TEST_RECORDS)]

ES_MOVIES_TEST_DATA.extend([{
    'uuid': str(uuid.uuid4()),
    'title': 'STAR WARS: EPISODE IV - A NEW HOPE',
    'imdb_rating': 8.6,
    'description': 'The Imperial Forces',
    'genre': [
        {
            'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd', 'name': 'Adventure'
        },
        {
            'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', 'name': 'Action'
        },
        {
            'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Sci-Fi'
        },
        {
            'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd', 'name': 'Fantasy'
        }
    ],
    'actors_names': ['Mark Hamill', 'Harrison Ford', 'Carrie Fisher', 'Peter Cushing'],
    'writers_names': ['George Lucas'],
    'actors': [
        {
            'uuid': '26e83050-29ef-4163-a99d-b546cac208f8', 'full_name': 'Mark Hamill'
        },
        {
            'uuid': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1', 'full_name': 'Harrison Ford'
        },
        {
            'uuid': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358', 'full_name': 'Carrie Fisher'
        },
        {
            'uuid': 'e039eedf-4daf-452a-bf92-a0085c68e156', 'full_name': 'Peter Cushing'
        }
    ],
    'writers': [
        {
            'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'full_name': 'George Lucas'
        }
    ],
    'directors': [
        {
            'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'full_name': 'George Lucas'
        }
    ]
} for _ in range(ES_MOVIES_A_HALF_OF_TEST_RECORDS)]
)

ES_EXISTED_MOVIES_LAST = copy.deepcopy(ES_MOVIES_TEST_DATA[ES_MOVIES_NUMBER_OF_TEST_RECORDS - 1])
del ES_EXISTED_MOVIES_LAST['actors_names']
del ES_EXISTED_MOVIES_LAST['writers_names']
ES_EXISTED_MOVIES_LAST_UUID = ES_MOVIES_TEST_DATA[ES_MOVIES_NUMBER_OF_TEST_RECORDS - 1].get('uuid')
ES_EXISTED_MOVIES_FIRST = copy.deepcopy(ES_MOVIES_TEST_DATA[0])
del ES_EXISTED_MOVIES_FIRST['actors_names']
del ES_EXISTED_MOVIES_FIRST['writers_names']
ES_EXISTED_MOVIES_FIRST_UUID = ES_MOVIES_TEST_DATA[ES_MOVIES_A_HALF_OF_TEST_RECORDS - 1].get('uuid')
ES_ABSENT_MOVIES_UUID = str(uuid.uuid4())
ES_NOT_UUID = 13
ES_MOVIES_NOT_FOUND_BODY = {'detail': 'film not found'}


async def get_films_test_data(es_data):
    short_films_data = [{'uuid': film.get('uuid'),
                         'title': film.get('title'),
                         'imdb_rating': film.get('imdb_rating')}
                        for film in es_data]
    sorted_short_films_data = sorted(short_films_data, key=(lambda film: film.get('imdb_rating')))
    sorted_desc_short_films_data = sorted(short_films_data, key=(lambda film: -film.get('imdb_rating')))
    genre_to_filter = es_data[random.randint(0, len(es_data) - 1)].get('genre')[0].get('name')
    filtered_short_films_data = [{'uuid': film.get('uuid'),
                                  'title': film.get('title'),
                                  'imdb_rating': film.get('imdb_rating')}
                                 for film in
                                 list(filter(lambda film:
                                             genre_to_filter in [genre.get('name') for genre in
                                                                 film.get('genre')], es_data))]
    return (short_films_data, sorted_short_films_data, sorted_desc_short_films_data, genre_to_filter,
            filtered_short_films_data)


async def get_absent_genre(es_data):
    genres_lists = list(map(lambda film: [genre.get('name') for genre in film.get('genre')], es_data))
    list_merge = lambda ll: reduce(lambda a, b: a + b, ll, [])
    genres = list_merge(genres_lists)
    while True:
        genre = fake.word()
        if genre not in genres:
            return genre