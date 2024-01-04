import sys
from random import randint, sample
from typing import Callable
from uuid import uuid4

import aiohttp
import backoff
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from tests.functional.settings import BaseTestSettings, session_settings, backoff_settings


@pytest_asyncio.fixture(scope='session')
async def es_client() -> AsyncElasticsearch:
    client = AsyncElasticsearch(hosts=session_settings.es_host, verify_certs=False)
    yield client
    await client.close()


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_tries=backoff_settings.max_tries,
                      max_time=backoff_settings.max_time)
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
    await client.aclose()


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_tries=backoff_settings.max_tries,
                      max_time=backoff_settings.max_time)
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


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_tries=backoff_settings.max_tries,
                      max_time=backoff_settings.max_time)
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


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_tries=backoff_settings.max_tries,
                      max_time=backoff_settings.max_time)
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


@backoff.on_exception(backoff.expo,
                      Exception,
                      max_tries=backoff_settings.max_tries,
                      max_time=backoff_settings.max_time)
@pytest.fixture
def get_all_records(make_get_request):
    async def inner(settings: BaseTestSettings, url: str, page_size: int, limit: int) -> list[dict]:
        query_data = {'page_size': page_size, 'page_number': 1}

        result = []
        while True:
            response = await make_get_request(url, settings, **query_data)
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

    return inner


POSSIBLE_GENRES = ['actor', 'writer', 'director']


@pytest.fixture
def faker_seed():
    return randint(0, sys.maxsize)


@pytest.fixture
def generate_genre_index(faker):
    async def inner(quantity: int = None) -> list[dict[str, str]]:
        return list([{
            'uuid': str(uuid4()),
            'name':  faker.word(),
        } for _ in range(quantity or 100)])

    return inner


@pytest.fixture()
def generate_person_names(faker):
    async def inner(quantity: int = None) -> list[dict[str, str]]:
        return list([{
            'uuid': str(uuid4()),
            'full_name': faker.name(),
        } for _ in range(quantity or 1000)])

    return inner


@pytest.fixture
def generate_movie_names(faker):
    async def inner(quantity: int = None) -> list[dict[str, str]]:
        return list([{
            'uuid': str(uuid4()),
            'title': faker.sentence()
        } for _ in range(quantity or 1000)])

    return inner


@pytest.fixture
def generate_movies_index(faker, generate_genre_index, generate_movie_names, generate_person_names):
    async def inner(
            quantity: int = None, *,
            genres_limit: int = 3, actors_limit: int = 10, writers_limit: int = 3, directors_limit: int = 3
    ) -> list[dict[str, str | dict]]:
        persons = await generate_person_names(quantity=quantity*max([actors_limit, writers_limit, directors_limit])//2)
        return list([{
            **movie,
            'imdb_rating': faker.pyfloat(positive=True, max_value=10, right_digits=2),
            'description': faker.paragraph(),
            'genre': sample(await generate_genre_index(), randint(1, genres_limit)),
            'actors': sample(persons, randint(1, actors_limit)),
            'writers': sample(persons, randint(1, writers_limit)),
            'directors': sample(persons, randint(1, directors_limit)),
        } for movie in (await generate_movie_names(quantity))])

    return inner


@pytest.fixture
def generate_persons_index(generate_person_names, generate_movie_names):
    async def inner(
            movies_index: list, quantity: int, *, films_limit: int = 20
    ) -> list[dict[str, str | list[str] | list[dict[str, str]]]]:
        roles = POSSIBLE_GENRES
        return list([{
            **person,
            'films': list(map(
                lambda film: {
                    'uuid': film['uuid'],
                    'roles': sample(roles, randint(1, len(roles)))
                }, sample(movies_index, randint(1, films_limit))
            )),
        } for person in (await generate_person_names(quantity))])
        pass

    return inner
