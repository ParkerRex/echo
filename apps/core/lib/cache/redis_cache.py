"""
RedisCache: Async Redis cache utility for Echo backend.

- Uses redis-py (asyncio) for non-blocking cache operations.
- Connects using settings from the central Settings object.
- Provides async get/set methods with TTL support.
- Designed for dependency injection and stateless usage.

Directory: apps/core/lib/cache/redis_cache.py
Layer: Infrastructure/Lib
"""

from typing import Any, Optional

import redis.asyncio as aioredis

from apps.core.core.config import settings


class RedisCache:
    """
    Async Redis cache utility for storing and retrieving values with TTL.
    """

    def __init__(self):
        self._client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=getattr(settings, "REDIS_DB", 0),
            password=getattr(settings, "REDIS_PASSWORD", None),
            decode_responses=True,
        )

    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from Redis by key.

        Args:
            key (str): The cache key.

        Returns:
            Optional[str]: The cached value, or None if not found.
        """
        return await self._client.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """
        Set a value in Redis with an optional TTL.

        Args:
            key (str): The cache key.
            value (Any): The value to cache (will be stringified).
            ttl_seconds (int): Time-to-live in seconds (default: 1 hour).
        """
        await self._client.set(key, str(value), ex=ttl_seconds)

    async def close(self):
        """
        Close the Redis connection.
        """
        await self._client.close()
