import pytest
import random

from http import HTTPStatus
from uuid import uuid4

from settings import person_test_settings, film_test_settings


async def prepare_indexes(generate_movies_index, generate_persons_index, es_write_data):
    movies_index = await generate_movies_index(random.randint(1, 1000))
    await es_write_data(movies_index, film_test_settings)
    persons_index = await generate_persons_index(movies_index, random.randint(1, 10000))
    await es_write_data(persons_index, person_test_settings)
    return movies_index, persons_index


async def check_valid_requests_person_get(person_ids, persons_index, make_get_request):
    for ind in person_ids:
        person = persons_index[ind]
        response = await make_get_request(f'/api/v1/persons/{person["uuid"]}', person_test_settings)
        assert response['status'] == HTTPStatus.OK
        assert response['body'] == person


@pytest.mark.asyncio(scope="session")
async def test_person_get(
        es_write_data, redis_flush_db, make_get_request, es_drop_index, generate_movies_index, generate_persons_index
):
    # 1. Подготовка данных.
    movies_index, persons_index = await prepare_indexes(generate_movies_index, generate_persons_index, es_write_data)

    person_ids = [random.randint(0, len(persons_index)-1) for _ in range(1, 20)]

    # 2. Тестирование получения неверных данных по API.
    for tid in [str(uuid4()) for _ in range(1, 20)]:
        response = await make_get_request(f'/api/v1/persons/{tid}', person_test_settings)
        assert response['status'] == HTTPStatus.NOT_FOUND

    # 3. Тестирование получения верных данных по API.
    await redis_flush_db()
    await check_valid_requests_person_get(person_ids, persons_index, make_get_request)

    # 4. Тестирование получения верных данных из кэша.
    await es_drop_index(person_test_settings)
    await check_valid_requests_person_get(person_ids, persons_index, make_get_request)


async def check_valid_requests_person_get_films(person_ids, persons_index, make_get_request, movies):
    for ind in person_ids:
        person = persons_index[ind]
        response = await make_get_request(f'/api/v1/persons/{person["uuid"]}/film', person_test_settings)
        assert response['status'] == 200
        assert sorted(response['body'], key=lambda film: film['uuid']) == sorted(
            list([movies[film['uuid']] for film in person['films']]), key=lambda film: film['uuid']
        )


@pytest.mark.asyncio(scope="session")
async def test_person_get_films(
        es_write_data, redis_flush_db, make_get_request, generate_movies_index, generate_persons_index, es_drop_index
):
    # 1. Подготовка данных.
    movies_index, persons_index = await prepare_indexes(generate_movies_index, generate_persons_index, es_write_data)

    person_ids = [random.randint(0, len(persons_index) - 1) for _ in range(1, 20)]

    movies = dict({movie['uuid']: {
        'uuid': movie['uuid'],
        'title': movie['title'],
        'imdb_rating': movie['imdb_rating']
    } for movie in movies_index})

    # 2. Тестирование получения неверных данных по API.
    for tid in [str(uuid4()) for _ in range(1, 20)]:
        response = await make_get_request(f'/api/v1/persons/{tid}/film', person_test_settings)
        assert response['status'] == HTTPStatus.NOT_FOUND

    # 3. Тестирование получения верных данных по API.
    await redis_flush_db()
    await check_valid_requests_person_get_films(person_ids, persons_index, make_get_request, movies)

    # 4. Тестирование получения верных данных из кэша.
    await es_drop_index(person_test_settings)
    await check_valid_requests_person_get_films(person_ids, persons_index, make_get_request, movies)
