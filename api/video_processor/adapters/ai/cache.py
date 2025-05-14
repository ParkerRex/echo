"""Caching layer for AI service responses."""

import hashlib
import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

from google.cloud import storage

from video_processor.infrastructure.monitoring import structured_log

# Type variable for decorator functions
F = TypeVar("F", bound=Callable[..., Any])

# Default cache location
DEFAULT_CACHE_DIR = Path(os.environ.get("AI_CACHE_DIR", "/tmp/ai_cache"))

# Cache invalidation time (default: 30 days)
DEFAULT_CACHE_TTL = int(
    os.environ.get("AI_CACHE_TTL", 60 * 60 * 24 * 30)
)  # 30 days in seconds

# Global cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "stores": 0,
    "errors": 0,
}


class AIResponseCache:
    """Cache for AI service responses."""

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        ttl: int = DEFAULT_CACHE_TTL,
        gcs_bucket: Optional[str] = None,
        prefix: str = "ai_cache",
    ):
        """Initialize cache.

        Args:
            cache_dir: Local directory for cache (default: /tmp/ai_cache)
            ttl: Cache TTL in seconds (default: 30 days)
            gcs_bucket: GCS bucket for remote cache (default: None)
            prefix: Prefix for remote cache keys (default: "ai_cache")
        """
        self.ttl = ttl
        self.gcs_bucket = gcs_bucket
        self.prefix = prefix

        # Set up local cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up GCS client if bucket specified
        self.gcs_client = None
        if gcs_bucket:
            try:
                self.gcs_client = storage.Client()
            except Exception as e:
                structured_log(
                    "error",
                    f"Failed to initialize GCS client for cache: {str(e)}",
                    {"error": str(e)},
                )

    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate a cache key from prompt and parameters.

        Args:
            prompt: Prompt text
            **kwargs: Additional parameters affecting the response

        Returns:
            Cache key
        """
        # Generate a stable cache key based on prompt and parameters
        key_data = {"prompt": prompt}

        # Add other parameters that affect the output
        for param_name in sorted(kwargs.keys()):
            param_value = kwargs[param_name]

            # Skip irrelevant parameters
            if param_name in ["api_key", "timeout"]:
                continue

            # Handle different parameter types
            if isinstance(param_value, (str, int, float, bool, type(None))):
                key_data[param_name] = param_value
            elif isinstance(param_value, (list, dict, tuple, set)):
                # Convert to JSON string for hashing
                key_data[param_name] = json.dumps(param_value, sort_keys=True)

        # Convert to string and hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def _get_local_cache_path(self, cache_key: str) -> Path:
        """Get local file path for cache key.

        Args:
            cache_key: Cache key

        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def _get_gcs_cache_path(self, cache_key: str) -> str:
        """Get GCS object path for cache key.

        Args:
            cache_key: Cache key

        Returns:
            GCS object path
        """
        return f"{self.prefix}/{cache_key}.json"

    def get(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response for prompt and parameters.

        Args:
            prompt: Prompt text
            **kwargs: Additional parameters affecting the response

        Returns:
            Cached response or None if not found
        """
        cache_key = self._generate_cache_key(prompt, **kwargs)

        # Try to get from local cache first
        local_path = self._get_local_cache_path(cache_key)
        if local_path.exists():
            try:
                with open(local_path, "r") as f:
                    cache_data = json.load(f)

                # Check if cache is expired
                if time.time() - cache_data.get("cached_at", 0) > self.ttl:
                    structured_log(
                        "info",
                        f"Cache expired for key {cache_key}",
                        {"cache_key": cache_key},
                    )
                    return None

                # Record cache hit
                _cache_stats["hits"] += 1

                structured_log(
                    "info",
                    f"Cache hit for key {cache_key}",
                    {"cache_key": cache_key},
                )

                return cache_data.get("response")

            except Exception as e:
                structured_log(
                    "error",
                    f"Failed to read from local cache: {str(e)}",
                    {"cache_key": cache_key, "error": str(e)},
                )
                _cache_stats["errors"] += 1

        # Try to get from GCS if available
        if self.gcs_client and self.gcs_bucket:
            try:
                bucket = self.gcs_client.bucket(self.gcs_bucket)
                blob = bucket.blob(self._get_gcs_cache_path(cache_key))

                if blob.exists():
                    cache_data = json.loads(blob.download_as_string())

                    # Check if cache is expired
                    if time.time() - cache_data.get("cached_at", 0) > self.ttl:
                        structured_log(
                            "info",
                            f"GCS cache expired for key {cache_key}",
                            {"cache_key": cache_key},
                        )
                        return None

                    # Store in local cache
                    try:
                        with open(local_path, "w") as f:
                            json.dump(cache_data, f)
                    except Exception as e:
                        structured_log(
                            "error",
                            f"Failed to store GCS cache locally: {str(e)}",
                            {"cache_key": cache_key, "error": str(e)},
                        )

                    # Record cache hit
                    _cache_stats["hits"] += 1

                    structured_log(
                        "info",
                        f"GCS cache hit for key {cache_key}",
                        {"cache_key": cache_key},
                    )

                    return cache_data.get("response")

            except Exception as e:
                structured_log(
                    "error",
                    f"Failed to read from GCS cache: {str(e)}",
                    {"cache_key": cache_key, "error": str(e)},
                )
                _cache_stats["errors"] += 1

        # Record cache miss
        _cache_stats["misses"] += 1

        return None

    def store(
        self,
        prompt: str,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Store response in cache.

        Args:
            prompt: Prompt text
            response: Response to cache
            metadata: Additional metadata to store
            **kwargs: Additional parameters affecting the response
        """
        cache_key = self._generate_cache_key(prompt, **kwargs)

        # Prepare cache data
        cache_data = {
            "prompt": prompt,
            "response": response,
            "cached_at": time.time(),
            "metadata": metadata or {},
            "parameters": {
                k: v for k, v in kwargs.items() if k not in ["api_key", "timeout"]
            },
        }

        # Store in local cache
        local_path = self._get_local_cache_path(cache_key)
        try:
            with open(local_path, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            structured_log(
                "error",
                f"Failed to write to local cache: {str(e)}",
                {"cache_key": cache_key, "error": str(e)},
            )
            _cache_stats["errors"] += 1
            return

        # Store in GCS if available
        if self.gcs_client and self.gcs_bucket:
            try:
                bucket = self.gcs_client.bucket(self.gcs_bucket)
                blob = bucket.blob(self._get_gcs_cache_path(cache_key))
                blob.upload_from_string(json.dumps(cache_data))

                structured_log(
                    "info",
                    f"Stored response in GCS cache for key {cache_key}",
                    {"cache_key": cache_key},
                )

            except Exception as e:
                structured_log(
                    "error",
                    f"Failed to write to GCS cache: {str(e)}",
                    {"cache_key": cache_key, "error": str(e)},
                )
                _cache_stats["errors"] += 1
                return

        # Record cache store
        _cache_stats["stores"] += 1

        structured_log(
            "info",
            f"Stored response in cache for key {cache_key}",
            {"cache_key": cache_key},
        )


# Create a global cache instance
_global_cache = AIResponseCache(
    gcs_bucket=os.environ.get("AI_CACHE_BUCKET"),
)


def get_global_cache() -> AIResponseCache:
    """Get the global cache instance.

    Returns:
        Global cache instance
    """
    return _global_cache


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics.

    Returns:
        Cache statistics
    """
    return _cache_stats.copy()


def use_cache(func: F) -> F:
    """Decorator for caching AI service responses.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the first argument is a prompt or text
        prompt = None
        if args and isinstance(args[0], str):
            prompt = args[0]
        elif "prompt" in kwargs and isinstance(kwargs["prompt"], str):
            prompt = kwargs["prompt"]
        elif "text" in kwargs and isinstance(kwargs["text"], str):
            prompt = kwargs["text"]

        # If we have a prompt, try to get from cache
        if prompt:
            cache = get_global_cache()
            cached_response = cache.get(prompt, **kwargs)

            if cached_response is not None:
                return cached_response

        # If not in cache or no prompt, call the original function
        response = func(*args, **kwargs)

        # Store in cache if we have a prompt and response
        if prompt and response:
            cache = get_global_cache()
            cache.store(prompt, response, **kwargs)

        return response

    return cast(F, wrapper)


def clear_cache(cache_dir: Optional[Union[str, Path]] = None) -> None:
    """Clear the cache.

    Args:
        cache_dir: Local directory to clear (default: DEFAULT_CACHE_DIR)
    """
    cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR

    if cache_dir.exists():
        # Remove all cache files
        for file_path in cache_dir.glob("*.json"):
            try:
                file_path.unlink()
            except Exception as e:
                structured_log(
                    "error",
                    f"Failed to delete cache file {file_path}: {str(e)}",
                    {"file_path": str(file_path), "error": str(e)},
                )

        structured_log(
            "info",
            f"Cleared local cache in {cache_dir}",
            {"cache_dir": str(cache_dir)},
        )
