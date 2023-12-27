from abc import ABC, abstractmethod
from pydantic import UUID4


class DataBase(ABC):

    @abstractmethod
    async def get(self, source: str, id_: UUID4, return_class: object.__class__) -> object.__class__ | None:
        pass

    @abstractmethod
    async def search(self, source: str, return_class: object.__class__, search_field: str | None = None,
                     search_string: str | None = None, filter_field: str | None = None,
                     filter_string: str | None = None, sort: str | None = None, page: int | None = 1,
                     per_page: int | None = 1) -> list | None:
        pass

    @abstractmethod
    async def ping(self):
        pass

    @abstractmethod
    async def close(self):
        pass


db: DataBase | None = None


async def get_db() -> DataBase:
    return db
