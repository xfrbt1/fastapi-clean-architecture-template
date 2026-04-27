from typing import Protocol


class CachePort(Protocol):
    """Key-value cache with optional TTL."""

    async def get(self, key: str) -> bytes | None:
        """Return raw bytes or None if missing."""

    async def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None:
        """Set value with optional expiration."""

    async def delete(self, key: str) -> None:
        """Remove key if present."""

    async def ping(self) -> bool:
        """Return True if cache backend is reachable."""
