from abc import ABC, abstractmethod


class Cache(ABC):

    @abstractmethod
    async def get(self, name: bytes | str, return_class: object.__class__) -> object.__class__ | None:
        pass

    @abstractmethod
    async def get_list(self, name: bytes | str, return_class: object.__class__) -> list | None:
        pass

    @abstractmethod
    async def set(self, name: bytes | str, value: object, ex: int | None = None) -> None:
        pass

    @abstractmethod
    async def ping(self):
        pass

    @abstractmethod
    async def close(self):
        pass


cache: Cache | None = None


async def get_cache() -> Cache:
    return cache
