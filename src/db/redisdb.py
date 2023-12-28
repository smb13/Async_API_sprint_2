from orjson import orjson
from redis.asyncio import Redis

from db.cache import Cache


class RedisDb(Cache):

    def __init__(self, cache_instance: Redis):
        self.cache_instance = cache_instance

    async def get(self, name: bytes | str, return_class: object.__class__) -> object.__class__ | None:
        data = await self.cache_instance.get(name)
        if not data:
            return None

        item = return_class.model_validate_json(data)
        return item

    async def get_list(self, name: bytes | str, return_class: object.__class__) -> list | None:
        data = await self.cache_instance.get(name)
        if not data:
            return None

        return [return_class.model_validate_json(item) for item in orjson.loads(data)]

    async def set(self, name: bytes | str, value: bytes | str | int | float, ex: int | None = None) -> None:
        await self.cache_instance.set(
            name=name,
            value=value,
            ex=ex
        )

    async def ping(self):
        await self.cache_instance.ping()

    async def close(self):
        await self.cache_instance.close()
