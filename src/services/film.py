from functools import lru_cache

import orjson
from fastapi import Depends
from pydantic import UUID4

from db.cache import Cache, get_cache
from db.database import DataBase, get_db
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    """
    FilmService содержит бизнес-логику по работе с фильмами.
    """
    def __init__(self, cache: Cache, db: DataBase):
        self.cache = cache
        self.db = db

    # Get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: UUID4) -> Film | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_db(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_film_to_cache(film)

        return film

    async def get_films(
            self, *, sort: str | None, genre: str | None = None,
            page: int | None = 1, per_page: int | None = 1, query: str | None = None
    ) -> list[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее.
        films = await self._films_list_from_cache(sort=sort, genre=genre, page=page, per_page=per_page, query=query)
        if not films:
            # Если фильмов нет в кеше, то ищем их в Elasticsearch
            films = await self._get_films_list_from_db(
                sort=sort, genre=genre, page=page, per_page=per_page, film=query
            )
            if not films:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return []
            # Сохраняем фильм в кеш
            await self._put_films_list_to_cache(sort=sort, genre=genre, page=page, per_page=per_page,
                                                query=query, films=films)

        return films

    async def _get_film_from_db(self, film_id: UUID4) -> Film | None:
        doc = await self.db.get(source='movies', id_=film_id, return_class=Film)
        return doc

    async def _get_films_list_from_db(
            self, *, sort: str | None, genre: str | None,
            page: int | None = 1, per_page: int | None = 1, film: str | None = None
    ) -> list[Film] | None:
        # Проверка аргументов.
        if page <= 0:
            page = 1
        if per_page <= 0:
            per_page = 1
        doc = await self.db.search(
            source='movies',
            search_field='title',
            search_string=film,
            filter_field='genre.name',
            filter_string=genre,
            sort=sort,
            page=page,
            per_page=per_page,
            return_class=Film
        )
        return doc

    async def _film_from_cache(self, film_id: UUID4) -> Film | None:
        film = await self.cache.get(name="movie:" + str(film_id), return_class=Film)
        return film

    async def _films_list_from_cache(self, **kwargs) -> list[Film] | None:
        films_list = await self.cache.get_list(
            name="movies:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            return_class=Film)
        return films_list

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме в кэше, указывая время жизни.
        await self.cache.set(
            name="movie:" + str(film.uuid),
            value=film.model_dump_json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_films_list_to_cache(self, films: list[Film], **kwargs):
        await self.cache.set(
            name="movies:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            value=orjson.dumps([ob.model_dump_json() for ob in films]),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS
        )


# Get_film_service — это провайдер FilmService.
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтон)
@lru_cache()
def get_film_service(
        cache: Cache = Depends(get_cache),
        db: DataBase = Depends(get_db),
) -> FilmService:
    return FilmService(cache, db)
