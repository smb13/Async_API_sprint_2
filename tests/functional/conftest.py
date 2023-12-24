from typing import Callable

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from tests.functional.settings import BaseTestSettings, session_settings


@pytest_asyncio.fixture(scope='session')
async def es_client() -> AsyncElasticsearch:
    client = AsyncElasticsearch(hosts=session_settings.es_host, verify_certs=False)
    yield client
    await client.close()


@pytest.fixture(scope='session')
def es_drop_index(es_client) -> Callable:
    async def inner(settings: BaseTestSettings) -> None:
        if await es_client.indices.exists(index=settings.es_index):
            await es_client.indices.delete(index=settings.es_index)

    return inner


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> Redis:
    client = Redis(host=session_settings.redis_host, port=session_settings.redis_port)
    yield client
    await client.close()


@pytest_asyncio.fixture
def redis_flush_db(redis_client) -> Callable:
    async def inner() -> None:
        await redis_client.flushdb()

    return inner


@pytest_asyncio.fixture(scope='session')
async def http_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def es_write_data(es_client, es_drop_index) -> Callable:
    async def inner(data: list[dict], settings: BaseTestSettings) -> None:
        # 2. Загружаем данные в ES
        await es_drop_index(settings)
        await es_client.indices.create(
            index=settings.es_index,
            mappings=settings.es_index_mapping[settings.es_index],
            settings=settings.es_index_settings
        )

        prepared_query: list[dict] = []
        for row in data:
            prepared_query.extend(
                [{'index': {'_index': settings.es_index, '_id': row[settings.es_id_field]}}, row]
            )
        response = await es_client.bulk(operations=prepared_query, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def make_get_request(http_session):
    async def inner(url: str, settings: BaseTestSettings, **kwargs):
        async with http_session.get(
                settings.service_url + url, params={**kwargs}
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

        pass

    return inner
