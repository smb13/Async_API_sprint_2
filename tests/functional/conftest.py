import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host, verify_certs=False)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session')
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict]):
        # 2. Загружаем данные в ES
        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(
            index=test_settings.es_index,
            mappings=test_settings.es_index_mapping[test_settings.es_index],
            settings=test_settings.es_index_settings
        )

        prepared_query: list[dict] = []
        for row in data:
            prepared_query.extend(
                [{'index': {'_index': test_settings.es_index, '_id': row[test_settings.es_id_field]}}, row]
            )
        response = await es_client.bulk(operations=prepared_query, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

        pass

    return inner


@pytest.fixture
def make_get_request(http_session):
    async def inner(url: str, query: dict):
        async with http_session.get(
                test_settings.service_url + url, params={'query': query['search']}
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

        pass

    return inner
