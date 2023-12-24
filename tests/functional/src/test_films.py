import pytest

from tests.functional.settings import film_test_settings
from tests.functional.testdata.es_test_data import (ES_MOVIES_TEST_DATA, ES_EXISTED_MOVIES_LAST,
                                                    ES_EXISTED_MOVIES_LAST_UUID, ES_ABSENT_MOVIES_UUID,
                                                    ES_MOVIES_A_HALF_OF_TEST_RECORDS, ES_MOVIES_NOT_FOUND_BODY,
                                                    ES_NOT_UUID, ES_MOVIES_NUMBER_OF_TEST_RECORDS,
                                                    ES_EXISTED_MOVIES_FIRST)


@pytest.mark.parametrize(
    'es_data, query_data, expected_answer', [
        (ES_MOVIES_TEST_DATA, {'query': 'Wars', 'page_size': film_test_settings.page_size},
         {'status': 200, 'length': ES_MOVIES_A_HALF_OF_TEST_RECORDS}),
        (ES_MOVIES_TEST_DATA, {'query': 'Star', 'page_size': film_test_settings.page_size},
         {'status': 200, 'length': ES_MOVIES_NUMBER_OF_TEST_RECORDS}),
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
        (ES_MOVIES_TEST_DATA, ES_EXISTED_MOVIES_LAST_UUID, {'status': 200, 'length': 8}, ES_EXISTED_MOVIES_LAST),
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
         {'status': 200, 'length': ES_MOVIES_NUMBER_OF_TEST_RECORDS, 'fist_title': None, 'last_title': None}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1, 'genre': 'Fantasy'},
         {'status': 200, 'length': ES_MOVIES_A_HALF_OF_TEST_RECORDS, 'fist_title': None, 'last_title': None}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1, 'genre': 'Sci-Fi'},
         {'status': 200, 'length': ES_MOVIES_NUMBER_OF_TEST_RECORDS, 'fist_title': None, 'last_title': None}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1, 'genre': 'Animation'},
         {'status': 404, 'length': 1, 'fist_title': None, 'last_title': None}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1, 'sort': '-imdb_rating'},
         {'status': 200, 'length': ES_MOVIES_NUMBER_OF_TEST_RECORDS, 'fist_title': ES_EXISTED_MOVIES_LAST.get('title'),
         'last_title': ES_EXISTED_MOVIES_FIRST.get('title')}),
        (ES_MOVIES_TEST_DATA, {'page_size': film_test_settings.page_size, 'page_number': 1, 'sort': 'imdb_rating'},
         {'status': 200, 'length': ES_MOVIES_NUMBER_OF_TEST_RECORDS, 'fist_title': ES_EXISTED_MOVIES_FIRST.get('title'),
         'last_title': ES_EXISTED_MOVIES_LAST.get('title')})
    ]
)
@pytest.mark.asyncio(scope='session')
async def test_get_list(es_write_data, make_get_request, es_data: list[dict], query_data, expected_answer):
    await es_write_data(es_data, film_test_settings)

    response = await make_get_request(f'{film_test_settings.prefix}/', film_test_settings, **query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']
    if expected_answer['fist_title'] and expected_answer['last_title']:
        assert response['body'][0].get('title') == expected_answer['fist_title']
        assert response['body'][len(response['body']) - 1].get('title') == expected_answer['last_title']
