import random
import uuid

import pytest

from settings import genre_test_settings


@pytest.mark.asyncio(scope="session")
async def test_genre_list(
        es_write_data, es_drop_index, es_client, redis_flush_db, generate_genre_index, get_all_records
):
    # 1. Подготовка данных.
    es_data = await generate_genre_index()
    await es_write_data(es_data, genre_test_settings)

    page_size = random.randint(10, 50)

    # 2. Тестирование получения данных по API.
    await redis_flush_db()
    result = await get_all_records(genre_test_settings, '/api/v1/genres/', page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == es_data

    # 3. Тестирование получение данных из кэша.
    await es_drop_index(genre_test_settings)
    result = await get_all_records(genre_test_settings, '/api/v1/genres/', page_size, len(es_data))
    assert len(result) == len(es_data)
    assert result == es_data

    # 4. Очистка.
    await es_drop_index(genre_test_settings)
    await redis_flush_db()


async def check_valid_requests_genre_get(genre_ids, genre_index, make_get_request):
    for ind in genre_ids:
        genre = genre_index[ind]
        response = await make_get_request(f'/api/v1/genres/{genre["uuid"]}', genre_test_settings)
        assert response['status'] == 200
        assert response['body'] == genre


@pytest.mark.asyncio(scope="session")
async def test_genre_get(es_write_data, redis_flush_db, make_get_request, es_drop_index, generate_genre_index):
    # 1. Подготовка данных.
    genre_index = await generate_genre_index()
    await es_write_data(genre_index, genre_test_settings)

    genre_ids = [random.randint(0, len(genre_index)-1) for _ in range(1, 20)]
    invalid_uuids = [str(uuid.uuid4()) for _ in range(1, 20)]

    # 2. Тестирование получения неверных данных по API.
    for tid in invalid_uuids:
        response = await make_get_request(f'/api/v1/genres/{tid}', genre_test_settings)
        assert response['status'] == 404

    # 3. Тестирование получения верных данных по API.
    await redis_flush_db()
    await check_valid_requests_genre_get(genre_ids, genre_index, make_get_request)

    # 4. Тестирование получения верных данных из кэша.
    await es_drop_index(genre_test_settings)
    await check_valid_requests_genre_get(genre_ids, genre_index, make_get_request)
