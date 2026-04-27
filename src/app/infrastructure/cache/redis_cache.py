from redis.asyncio import Redis

from app.application.interfaces.cache import CachePort


class RedisCache(CachePort):
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get(self, key: str) -> bytes | None:
        raw = await self._client.get(key)
        if raw is None:
            return None
        return raw if isinstance(raw, bytes) else bytes(raw)

    async def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is not None:
            await self._client.set(key, value, ex=ttl_seconds)
        else:
            await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            return False
