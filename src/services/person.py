from functools import lru_cache

import orjson
from fastapi import Depends
from pydantic import UUID4

from db.cache import Cache, get_cache
from db.database import DataBase, get_db
from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    """
    PersonService содержит бизнес-логику по работе с персонами.
    """

    def __init__(self, cache: Cache, db: DataBase):
        self.cache = cache
        self.db = db

    # Get_by_id возвращает объект персоны. Он опционален, так как персона может отсутствовать в базе
    async def get_by_id(self, person_id: UUID4) -> Person | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._person_from_cache(person_id)
        if not person:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            person = await self._get_person_from_db(person_id)
            if not person:
                # Если он отсутствует в Elasticsearch, значит, персона вообще нет в базе
                return None
            # Сохраняем персону в кеш
            await self._put_person_to_cache(person)

        return person

    async def get_persons(
            self, *, page: int | None = 1,
            per_page: int | None = 1, query: str | None = None
    ) -> list[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее.
        persons = await self._persons_list_from_cache(page=page, per_page=per_page, query=query)
        if not persons:
            # Если персон нет в кеше, то ищем их в Elasticsearch
            persons = await self._get_persons_list_from_db(
                page=page, per_page=per_page, person=query
            )
            if not persons:
                # Если он отсутствует в Elasticsearch, значит, персон вообще нет в базе
                return []
            # Сохраняем персоны в кеш
            await self._put_persons_list_to_cache(page=page, per_page=per_page,
                                                  query=query, persons=persons)

        return persons

    async def _get_person_from_db(self, person_id: UUID4) -> Person | None:
        doc = await self.db.get(source='persons', id_=person_id, return_class=Person)
        return doc

    async def _get_persons_list_from_db(
            self, *, page: int | None = 1, per_page: int | None = 1, person: str | None = None
    ) -> list[Person] | None:
        # Проверка аргументов.
        if page <= 0:
            page = 1
        if per_page <= 0:
            per_page = 1
        doc = await self.db.search(
            source='persons',
            search_field='full_name',
            search_string=person,
            page=page,
            per_page=per_page,
            return_class=Person
        )
        return doc

    async def _person_from_cache(self, person_id: UUID4) -> Person | None:
        person = await self.cache.get(name="person:" + str(person_id), return_class=Person)
        return person

    async def _persons_list_from_cache(self, **kwargs) -> list[Person] | None:
        persons_list = await self.cache.get_list(
            name="persons:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            return_class=Person)
        return persons_list

    async def _put_person_to_cache(self, person: Person):
        # Сохраняем данные о персоне в кэше, указывая время жизни.
        await self.cache.set(
            name="person:" + str(person.uuid),
            value=person.model_dump_json(),
            ex=PERSON_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_persons_list_to_cache(self, persons: list[Person], **kwargs):
        await self.cache.set(
            name="persons:" + orjson.dumps(kwargs, option=orjson.OPT_SORT_KEYS).decode('utf-8'),
            value=orjson.dumps([ob.model_dump_json() for ob in persons]),
            ex=PERSON_CACHE_EXPIRE_IN_SECONDS
        )


# Get_person_service — это провайдер PersonService.
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтон)
@lru_cache()
def get_person_service(
        cache: Cache = Depends(get_cache),
        db: DataBase = Depends(get_db),
) -> PersonService:
    return PersonService(cache, db)
