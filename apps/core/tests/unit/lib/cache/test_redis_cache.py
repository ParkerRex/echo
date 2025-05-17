"""
Unit tests for the RedisCache class.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.core.lib.cache.redis_cache import RedisCache


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis async client."""
    with patch("redis.asyncio.Redis") as mock_redis:
        # Create AsyncMock instances for the Redis methods we'll use
        mock_client = AsyncMock()
        mock_client.get = AsyncMock()
        mock_client.set = AsyncMock()
        mock_client.close = AsyncMock()

        # Configure the Redis constructor to return our mock client
        mock_redis.return_value = mock_client

        # Return both the Redis constructor mock and the client mock for verification
        yield mock_redis, mock_client


class TestRedisCache:
    """Test cases for the RedisCache class."""

    def test_initialization(self, mock_redis_client):
        """Test initializing the RedisCache with settings."""
        mock_redis, mock_client = mock_redis_client

        # Initialize the cache
        cache = RedisCache()

        # Verify Redis client was initialized with the correct parameters
        mock_redis.assert_called_once()

        # Check the parameters (note: we can't check the exact values as they come from settings)
        args, kwargs = mock_redis.call_args
        assert "host" in kwargs
        assert "port" in kwargs
        assert "db" in kwargs
        assert "password" in kwargs
        assert kwargs["decode_responses"] is True

    @pytest.mark.asyncio
    async def test_get_existing_value(self, mock_redis_client):
        """Test retrieving an existing value from the cache."""
        mock_redis, mock_client = mock_redis_client

        # Configure the mock to return a specific value
        mock_client.get.return_value = "cached_value"

        # Initialize the cache and call get
        cache = RedisCache()
        result = await cache.get("test_key")

        # Verify get was called with the correct key
        mock_client.get.assert_called_once_with("test_key")

        # Verify the result
        assert result == "cached_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_value(self, mock_redis_client):
        """Test retrieving a non-existent value from the cache."""
        mock_redis, mock_client = mock_redis_client

        # Configure the mock to return None (key not found)
        mock_client.get.return_value = None

        # Initialize the cache and call get
        cache = RedisCache()
        result = await cache.get("nonexistent_key")

        # Verify get was called with the correct key
        mock_client.get.assert_called_once_with("nonexistent_key")

        # Verify the result is None
        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_default_ttl(self, mock_redis_client):
        """Test setting a value in the cache with the default TTL."""
        mock_redis, mock_client = mock_redis_client

        # Initialize the cache and call set
        cache = RedisCache()
        await cache.set("test_key", "test_value")

        # Verify set was called with the correct parameters
        mock_client.set.assert_called_once_with("test_key", "test_value", ex=3600)

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, mock_redis_client):
        """Test setting a value in the cache with a custom TTL."""
        mock_redis, mock_client = mock_redis_client

        # Initialize the cache and call set with a custom TTL
        cache = RedisCache()
        await cache.set("test_key", "test_value", ttl_seconds=600)

        # Verify set was called with the correct parameters
        mock_client.set.assert_called_once_with("test_key", "test_value", ex=600)

    @pytest.mark.asyncio
    async def test_set_non_string_value(self, mock_redis_client):
        """Test setting a non-string value in the cache (should be stringified)."""
        mock_redis, mock_client = mock_redis_client

        # Initialize the cache and call set with a non-string value
        cache = RedisCache()
        await cache.set("test_key", 123)

        # Verify set was called with the stringified value
        mock_client.set.assert_called_once_with("test_key", "123", ex=3600)

    @pytest.mark.asyncio
    async def test_close(self, mock_redis_client):
        """Test closing the Redis connection."""
        mock_redis, mock_client = mock_redis_client

        # Initialize the cache and call close
        cache = RedisCache()
        await cache.close()

        # Verify close was called
        mock_client.close.assert_called_once()
