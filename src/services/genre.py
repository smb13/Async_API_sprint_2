from functools import lru_cache

import orjson
from fastapi import Depends
from pydantic import UUID4

from db.cache import Cache, get_cache
from db.database import DataBase, get_db
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    """
    GenreService содержит бизнес-логику по работе с жанрами.
    """

    def __init__(self, cache: Cache, db: DataBase):
        self.cache = cache
        self.db = db

    # Get_by_id возвращает объект жанра. Он опционален, так как жанр может отсутствовать в базе
    async def get_by_id(self, genre_id: UUID4) -> Genre | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            # Если жанра нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_db(genre_id)
            if not genre:
                # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
                return None
            # Сохраняем жанр в кеш
            await self._put_genre_to_cache(genre)

        return genre

    async def get_genres(
            self, *, page: int | None = 1, per_page: int | None = 1
    ) -> list[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее.
        genres = await self._genres_list_from_cache(page=page, per_page=per_page)
        if not genres:
            # Если жанров нет в кеше, то ищем их в Elasticsearch
            genres = await self._get_genres_list_from_db(page=page, per_page=per_page
                                                         )
            if not genres:
                # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
                return []
            # Сохраняем жанр в кеш
            await self._put_genres_list_to_cache(page=page, per_page=per_page,
                                                 genres=genres)

        return genres

    async def _get_genre_from_db(self, genre_id: UUID4) -> Genre | None:
        doc = await self.db.get(source='genres', id_=genre_id, return_class=Genre)
        return doc

    async def _get_genres_list_from_db(
            self, *, page: int | None = 1, per_page: int | None = 1
    ) -> list[Genre] | None:
        # Проверка аргументов.
        if page <= 0:
            page = 1
        if per_page <= 0:
            per_page = 1
        doc = await self.db.search(
            source='genres',
            page=page,
            per_page=per_page,
            return_class=Genre
        )
        return doc

    async def _genre_from_cache(self, genre_id: UUID4) -> Genre | None:
        genre = await self.cache.get(name="genre:" + str(genre_id), return_class=Genre)
        return genre

    async def _genres_list_from_cache(self, **kwargs) -> list[Genre] | None:
        genres_list = await self.cache.get_list(
            name="genres:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            return_class=Genre)
        return genres_list

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные о жанре в кэше, указывая время жизни.
        await self.cache.set(
            name="genre:" + str(genre.uuid),
            value=genre.model_dump_json(),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_genres_list_to_cache(self, genres: list[Genre], **kwargs):
        await self.cache.set(
            name="genres:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            value=orjson.dumps([ob.model_dump_json() for ob in genres]),
            ex=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


# Get_genre_service — это провайдер GenreService.
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтон)
@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_cache),
        db: DataBase = Depends(get_db),
) -> GenreService:
    return GenreService(cache, db)
