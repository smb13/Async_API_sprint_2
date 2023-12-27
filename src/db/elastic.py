from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import UUID4

from db.database import DataBase


class Elastic(DataBase):

    def __init__(self, db_instance: AsyncElasticsearch):
        self.db_instance = db_instance

    async def get(self, source: str, id_: UUID4, return_class: object.__class__) -> object.__class__ | None:
        try:
            doc = await self.db_instance.get(index=source, id=id_)
        except NotFoundError:
            return None
        return return_class(**doc['_source'])

    async def search(self, source: str, return_class: object.__class__, search_field: str | None = None,
                     search_string: str | None = None, filter_field: str | None = None,
                     filter_string: str | None = None, sort: str | None = None, page: int | None = 1,
                     per_page: int | None = 1) -> list | None:
        try:
            must = []
            if filter_field and filter_string:
                must.append({
                    "nested": {"path": filter_field.split('.')[0],
                               "query": {"bool": {"must": [{"match": {filter_field: filter_string}}]}}}
                })
            if search_field and search_string:
                must.append({"match": {search_field: search_string}})
            doc = await self.db_instance.search(
                index=source,
                body={"query": {"bool": {"must": must}}},
                from_=(page - 1) * per_page,
                size=per_page,
                sort=(sort[1:] + ":desc" if sort[0] == '-' else sort) if sort else None
            )
        except NotFoundError:
            return None
        return list(map(lambda item: return_class(**item['_source']), doc['hits']['hits']))

    async def ping(self):
        await self.db_instance.ping()

    async def close(self):
        await self.db_instance.close()
