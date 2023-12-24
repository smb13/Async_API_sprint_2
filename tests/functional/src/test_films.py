import pytest

from tests.functional.settings import film_test_settings
from tests.functional.testdata.es_test_data import (ES_MOVIES_TEST_DATA, ES_EXISTED_MOVIES, ES_EXISTED_MOVIES_UUID,
                                                    ES_ABSENT_MOVIES_UUID, ES_MOVIES_A_HALF_OF_TEST_RECORDS,
                                                    ES_MOVIES_NOT_FOUND_BODY, ES_NOT_UUID)


@pytest.mark.parametrize(
    'es_data, query_data, expected_answer', [
        (ES_MOVIES_TEST_DATA, {'query': 'Wars', 'page_size': film_test_settings.page_size},
         {'status': 200, 'length': ES_MOVIES_A_HALF_OF_TEST_RECORDS}),
        (ES_MOVIES_TEST_DATA, {'query': 'Star', 'page_size': film_test_settings.page_size},
         {'status': 200, 'length': film_test_settings.page_size}),
        (ES_MOVIES_TEST_DATA, {'query': 'Mashed potato', 'page_size': film_test_settings.page_size},
         {'status': 404, 'length': 1}),
        (ES_MOVIES_TEST_DATA, {'query': 13, 'page_size': film_test_settings.page_size},
         {'status': 404, 'length': 1})
    ]
)
@pytest.mark.asyncio(scope='session')
async def test_search(es_write_data, make_get_request, es_data: list[dict], query_data, expected_answer):
    await es_write_data(es_data, film_test_settings)

    response = await make_get_request(f'{film_test_settings.prefix}/search', film_test_settings, **query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']


@pytest.mark.parametrize(
    'es_data, film_id, expected_answer, expected_body', [
        (ES_MOVIES_TEST_DATA, ES_EXISTED_MOVIES_UUID, {'status': 200, 'length': 8}, ES_EXISTED_MOVIES),
        (ES_MOVIES_TEST_DATA, ES_ABSENT_MOVIES_UUID, {'status': 404, 'length': 1}, ES_MOVIES_NOT_FOUND_BODY),
        (ES_MOVIES_TEST_DATA, ES_NOT_UUID, {'status': 422, 'length': 1}, None)
    ]
)
@pytest.mark.asyncio(scope='session')
async def test_get_byid(es_write_data, make_get_request, es_data: list[dict], film_id, expected_answer, expected_body):
    await es_write_data(es_data, film_test_settings)

    response = await make_get_request(f'{film_test_settings.prefix}/{film_id}', film_test_settings)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
    if expected_body:
        assert response['body'] == expected_body


@pytest.mark.parametrize(
    'es_data, query_data, expected_answer', [
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1},
         {'status': 200, 'length': film_test_settings.page_size}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size,
                               'page_number': (ES_MOVIES_A_HALF_OF_TEST_RECORDS * 2) // film_test_settings.page_size +
                               1},
         {'status': 200, 'length': (ES_MOVIES_A_HALF_OF_TEST_RECORDS * 2) % film_test_settings.page_size})
    ]
)
@pytest.mark.asyncio(scope='session')
async def test_get_list(es_write_data, make_get_request, es_data: list[dict], query_data, expected_answer):
    await es_write_data(es_data, film_test_settings)

    response = await make_get_request(f'{film_test_settings.prefix}/', film_test_settings, **query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
