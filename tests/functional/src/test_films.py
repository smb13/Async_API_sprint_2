import random
import uuid

import pytest

from testdata.films_test_data import get_films_test_data, get_absent_genre
from settings import film_test_settings


async def prepare_index(generate_movies_index, es_write_data):
    movies_index = await generate_movies_index(random.randint(1, 1000))
    await es_write_data(movies_index, film_test_settings)
    return movies_index


@pytest.mark.asyncio(scope="session")
async def test_films_list(
        es_write_data, es_drop_index, es_client, redis_flush_db, generate_movies_index, get_all_records,
        make_get_request):
    # 1. Подготовка данных.
    es_data = await prepare_index(generate_movies_index, es_write_data)

    (short_films_data, sorted_short_films_data, sorted_desc_short_films_data, genre_to_filter,
     filtered_short_films_data) = await get_films_test_data(es_data)

    absent_genre = await get_absent_genre()

    page_size = random.randint(10, 50)

    # 2. Тестирование получения данных по API.
    await redis_flush_db()

    result = await get_all_records(film_test_settings, '/api/v1/films/', page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == short_films_data

    result = await get_all_records(film_test_settings, '/api/v1/films/?sort=imdb_rating', page_size, len(es_data))
    assert result == sorted_short_films_data
    assert len(result) == len(sorted_short_films_data)

    result = await get_all_records(film_test_settings, '/api/v1/films/?sort=-imdb_rating', page_size, len(es_data))
    assert result == sorted_desc_short_films_data
    assert len(result) == len(sorted_desc_short_films_data)

    result = await get_all_records(film_test_settings, f'/api/v1/films/?genre={genre_to_filter}', page_size,
                                   len(es_data))
    assert result == filtered_short_films_data
    assert len(result) == len(filtered_short_films_data)

    response = await make_get_request(f'/api/v1/films/?genre={absent_genre}', film_test_settings)
    assert response['status'] == 404

    # 3. Тестирование получение данных из кэша.
    await es_drop_index(film_test_settings)
    result = await get_all_records(film_test_settings, '/api/v1/films/', page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == short_films_data

    result = await get_all_records(film_test_settings, '/api/v1/films/?sort=imdb_rating', page_size, len(es_data))
    assert result == sorted_short_films_data
    assert len(result) == len(sorted_short_films_data)

    result = await get_all_records(film_test_settings, '/api/v1/films/?sort=-imdb_rating', page_size, len(es_data))
    assert result == sorted_desc_short_films_data
    assert len(result) == len(sorted_desc_short_films_data)

    result = await get_all_records(film_test_settings, f'/api/v1/films/?genre={genre_to_filter}', page_size,
                                   len(es_data))
    assert result == filtered_short_films_data
    assert len(result) == len(filtered_short_films_data)

    response = await make_get_request(f'/api/v1/films/?genre={absent_genre}', film_test_settings)
    assert response['status'] == 404

    # 4. Очистка.
    await es_drop_index(film_test_settings)
    await redis_flush_db()


async def check_valid_requests_film_get(film_ids, film_index, make_get_request):
    for ind in film_ids:
        film = film_index[ind]
        response = await make_get_request(f'/api/v1/films/{film["uuid"]}', film_test_settings)
        assert response['status'] == 200
        assert response['body'] == film


@pytest.mark.asyncio(scope="session")
async def test_films_get(es_write_data, redis_flush_db, make_get_request, es_drop_index, generate_movies_index):
    # 1. Подготовка данных.
    film_index = await prepare_index(generate_movies_index, es_write_data)

    film_ids = [random.randint(0, len(film_index) - 1) for _ in range(1, 20)]
    invalid_uuids = [str(uuid.uuid4()) for _ in range(1, 20)]

    # 2. Тестирование получения неверных данных по API.
    for tid in invalid_uuids:
        response = await make_get_request(f'/api/v1/films/{tid}', film_test_settings)
        assert response['status'] == 404

    # 3. Тестирование получения верных данных по API.
    await redis_flush_db()
    await check_valid_requests_film_get(film_ids, film_index, make_get_request)

    # 4. Тестирование получения верных данных из кэша.
    await es_drop_index(film_test_settings)
    await check_valid_requests_film_get(film_ids, film_index, make_get_request)
