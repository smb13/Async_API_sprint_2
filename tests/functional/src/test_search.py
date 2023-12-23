import uuid

import pytest

from tests.functional.settings import search_test_settings

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
    } for _ in range(60)]


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
