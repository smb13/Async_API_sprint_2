import random
import uuid
from typing import Callable

import pytest

from tests.functional.settings import genre_test_settings


async def get_all_genres(make_get_request: Callable, page_size: int, limit: int) -> list[dict]:
    query_data = {'page_size': page_size, 'page_number': 1}

    result = []
    while True:
        response = await make_get_request('/api/v1/genres/', genre_test_settings, **query_data)
        if response['status'] == 404:
            break

        assert response['status'] == 200
        assert len(response['body']) <= page_size
        if len(response['body']) == 0:
            break

        result.extend(list[dict](response['body']))
        assert len(result) <= limit
        query_data['page_number'] += 1

    return result


@pytest.mark.asyncio(scope="session")
async def test_genre_list(es_write_data, es_drop_index, make_get_request, es_client, redis_flush_db):
    # 1. Подготовка данных.
    es_data = list([{
        'uuid': str(uuid.uuid4()),
        'name': 'Comedy' + str(random.randint(1, 100000)),
    } for i in range(random.randint(1, 1000))])
    await es_write_data(es_data, genre_test_settings)

    page_size = random.randint(10, 50)

    # 2. Тестирование получения данных по API.
    await redis_flush_db()
    result = await get_all_genres(make_get_request, page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == es_data

    # 3. Тестирование получение данных из кэша.
    await es_drop_index(genre_test_settings)
    result = await get_all_genres(make_get_request, page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == es_data

    # 4. Очистка.
    await es_drop_index(genre_test_settings)
    await redis_flush_db()


@pytest.mark.asyncio(scope="session")
async def test_genre_get(es_write_data, redis_flush_db, make_get_request, es_drop_index):
    # 1. Подготовка данных.
    es_data = list([{
        'uuid': str(uuid.uuid4()),
        'name': 'Comedy' + str(random.randint(1, 100000)),
    } for i in range(random.randint(1, 1000))])
    await es_write_data(es_data, genre_test_settings)

    indexes = [random.randint(0, len(es_data)-1) for _ in range(1, 20)]
    invalid_uuids = [str(uuid.uuid4()) for _ in range(1, 20)]

    # 2. Тестирование получения неверных данных по API.
    for tid in invalid_uuids:
        response = await make_get_request(f'/api/v1/genres/{tid}', genre_test_settings)
        assert response['status'] == 404

    # 3. Тестирование получения верных данных по API.
    await redis_flush_db()
    for ind in indexes:
        row = es_data[ind]
        response = await make_get_request(f'/api/v1/genres/{row["uuid"]}', genre_test_settings)
        assert response['status'] == 200
        assert response['body'] == row

    # 4. Тестирование получения верных данных из кэша.
    await es_drop_index(genre_test_settings)
    for ind in indexes:
        row = es_data[ind]
        response = await make_get_request(f'/api/v1/genres/{row["uuid"]}', genre_test_settings)
        assert response['status'] == 200
        assert response['body'] == row
