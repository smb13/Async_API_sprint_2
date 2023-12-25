import sys
from random import sample, randint
from uuid import uuid4

import pytest


POSSIBLE_GENRES = ['actor', 'writer', 'director']


@pytest.fixture
def faker_seed():
    return randint(0, sys.maxsize)


@pytest.fixture
def generate_genre_names(faker):
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


@pytest.fixture()
def generate_movie_names(faker):
    async def inner(quantity: int = None) -> list[dict[str, str]]:
        return list([{
            'uuid': str(uuid4()),
            'title': faker.sentence()
        } for _ in range(quantity or 1000)])

    return inner


@pytest.fixture
def generate_movies_index(faker, generate_genre_names, generate_movie_names, generate_person_names):
    async def inner(
            quantity: int = None, *,
            genres_limit: int = 3, actors_limit: int = 10, writers_limit: int = 3, directors_limit: int = 3
    ) -> list[dict[str, str | dict]]:
        persons = await generate_person_names(quantity=quantity*max([actors_limit, writers_limit, directors_limit])//2)
        return list([{
            **movie,
            'imdb_rating': faker.pyfloat(positive=True, max_value=10, right_digits=2),
            'description': faker.paragraph(),
            'genre': sample(await generate_genre_names(), randint(1, genres_limit)),
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
