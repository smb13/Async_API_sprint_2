import random

import pytest

from testdata.persons_test_data import get_persons_search_test_data, persons_search_es_data
from settings import film_test_settings, person_test_settings
from testdata.films_test_data import (get_films_search_test_data, films_search_es_data)


async def prepare_persons_index(es_write_data):
    persons_index = persons_search_es_data
    await es_write_data(persons_index, person_test_settings)
    return persons_index


async def prepare_movies_index(es_write_data):
    movies_index = films_search_es_data
    await es_write_data(movies_index, film_test_settings)
    return movies_index


@pytest.mark.asyncio(scope="session")
async def test_films_search(
        es_write_data, es_drop_index, es_client, redis_flush_db, generate_movies_index, get_all_records):

    # 1. Подготовка данных.
    es_data = await prepare_movies_index(es_write_data)

    (word_to_search, absent_word, short_films_data, searched_short_films_data, searched_sorted_short_films_data,
     searched_sorted_desc_short_films_data) = await get_films_search_test_data(es_data)

    page_size = random.randint(10, 50)

    # 2. Тестирование получения данных по API.
    await redis_flush_db()

    result = await get_all_records(film_test_settings, '/api/v1/films/search/', page_size, len(short_films_data))
    assert len(result) == len(short_films_data)
    assert result == short_films_data

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={word_to_search}', page_size,
                                   len(es_data))
    assert len(result) == len(searched_short_films_data)
    assert sorted(result, key=(lambda film: film.get('title'))) == searched_short_films_data

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={word_to_search}&sort=imdb_rating',
                                   page_size, len(es_data))
    assert result == searched_sorted_short_films_data
    assert len(result) == len(searched_sorted_short_films_data)

    result = await get_all_records(film_test_settings,
                                   f'/api/v1/films/search/?query={word_to_search}&sort=-imdb_rating', page_size,
                                   len(es_data))
    assert result == searched_sorted_desc_short_films_data
    assert len(result) == len(searched_sorted_desc_short_films_data)

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={absent_word}', page_size,
                                   len(es_data))
    assert len(result) == 0

    # 3. Тестирование получение данных из кэша.
    await es_drop_index(film_test_settings)

    result = await get_all_records(film_test_settings, '/api/v1/films/search/', page_size, len(short_films_data))
    assert len(result) == len(short_films_data)
    assert result == short_films_data

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={word_to_search}', page_size,
                                   len(es_data))
    assert len(result) == len(searched_short_films_data)
    assert sorted(result, key=(lambda film: film.get('title'))) == searched_short_films_data

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={word_to_search}&sort=imdb_rating',
                                   page_size, len(es_data))
    assert result == searched_sorted_short_films_data
    assert len(result) == len(searched_sorted_short_films_data)

    result = await get_all_records(film_test_settings,
                                   f'/api/v1/films/search/?query={word_to_search}&sort=-imdb_rating', page_size,
                                   len(es_data))
    assert result == searched_sorted_desc_short_films_data
    assert len(result) == len(searched_sorted_desc_short_films_data)

    result = await get_all_records(film_test_settings, f'/api/v1/films/search/?query={absent_word}', page_size,
                                   len(es_data))
    assert len(result) == 0

    # 4. Очистка.
    await es_drop_index(film_test_settings)
    await redis_flush_db()


@pytest.mark.asyncio(scope="session")
async def test_persons_search(
        es_write_data, es_drop_index, es_client, redis_flush_db, generate_persons_index, get_all_records,
        make_get_request, generate_movies_index):
    # 1. Подготовка данных.
    persons_index = await prepare_persons_index(es_write_data)

    (word_to_search, absent_word, searched_persons_data) = await get_persons_search_test_data(persons_index)

    page_size = random.randint(10, 50)

    # 2. Тестирование получения данных по API.
    await redis_flush_db()

    result = await get_all_records(person_test_settings, '/api/v1/persons/search/', page_size, len(persons_index))
    assert len(result) == len(persons_index)
    assert result == persons_index

    result = await get_all_records(film_test_settings, f'/api/v1/persons/search/?query={word_to_search}', page_size,
                                   len(persons_index))
    assert len(result) == len(searched_persons_data)
    assert sorted(result, key=(lambda film: film.get('full_name'))) == searched_persons_data

    result = await get_all_records(film_test_settings, f'/api/v1/persons/search/?query={absent_word}', page_size,
                                   len(persons_index))
    assert len(result) == 0

    # 3. Тестирование получение данных из кэша.
    await es_drop_index(film_test_settings)

    result = await get_all_records(person_test_settings, '/api/v1/persons/search/', page_size, len(persons_index))
    assert len(result) == len(persons_index)
    assert result == persons_index

    result = await get_all_records(person_test_settings, f'/api/v1/persons/search/?query={word_to_search}', page_size,
                                   len(persons_index))
    assert len(result) == len(searched_persons_data)
    assert sorted(result, key=(lambda film: film.get('full_name'))) == searched_persons_data

    result = await get_all_records(person_test_settings, f'/api/v1/persons/search/?query={absent_word}', page_size,
                                   len(persons_index))
    assert len(result) == 0

    # 4. Очистка.
    await es_drop_index(film_test_settings)
    await redis_flush_db()
