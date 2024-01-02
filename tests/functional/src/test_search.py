import pytest

from tests.functional.settings import search_test_settings

from tests.functional.testdata.films_test_data import (ES_MOVIES_TEST_DATA)


@pytest.mark.parametrize(
    'es_data, query_data, expected_answer', [
        (ES_MOVIES_TEST_DATA, {'query': 'Star'}, {'status': 200, 'length': 50}),
        (ES_MOVIES_TEST_DATA, {'query': 'Mashed potato'}, {'status': 404, 'length': 1})
    ]
)
@pytest.mark.asyncio(scope='session')
async def test_search(es_write_data, make_get_request, es_data: list[dict], query_data, expected_answer):
    await es_write_data(es_data, search_test_settings)

    response = await make_get_request('/api/v1/films/search', search_test_settings, **query_data)

    assert response['status'] == expected_answer['status']
    assert len(response['body']) == expected_answer['length']