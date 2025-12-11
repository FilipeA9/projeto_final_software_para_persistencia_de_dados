"""
Redis cache connection and client management.

Provides Redis client for caching operations.
"""

from typing import Any, Optional
import json
from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.config.settings import settings

# Global Redis client
_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Get Redis client instance.
    
    Returns:
        Redis: Redis client for async operations.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
            encoding="utf-8",
        )
    return _redis_client


async def init_redis() -> None:
    """
    Initialize Redis connection and test connectivity.
    """
    client = get_redis_client()
    try:
        await client.ping()
        print("Redis connection established successfully")
    except RedisError as e:
        print(f"Redis connection failed: {e}")
        raise


async def close_redis() -> None:
    """Close Redis connection and cleanup resources."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        print("Redis connection closed")


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache by key.
    
    Args:
        key: Cache key.
    
    Returns:
        Cached value (JSON decoded) or None if not found.
    """
    client = get_redis_client()
    try:
        value = await client.get(key)
        if value is not None:
            return json.loads(value)
        return None
    except RedisError as e:
        print(f"Redis get error: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set value in cache with optional TTL.
    
    Args:
        key: Cache key.
        value: Value to cache (will be JSON encoded).
        ttl: Time to live in seconds (default: settings.REDIS_TTL).
    
    Returns:
        True if successful, False otherwise.
    """
    client = get_redis_client()
    try:
        ttl = ttl or settings.REDIS_TTL
        await client.setex(key, ttl, json.dumps(value))
        return True
    except RedisError as e:
        print(f"Redis set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """
    Delete value from cache by key.
    
    Args:
        key: Cache key to delete.
    
    Returns:
        True if successful, False otherwise.
    """
    client = get_redis_client()
    try:
        await client.delete(key)
        return True
    except RedisError as e:
        print(f"Redis delete error: {e}")
        return False


async def cache_clear_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.
    
    Args:
        pattern: Key pattern (e.g., "spot:*" to delete all spot keys).
    
    Returns:
        Number of keys deleted.
    """
    client = get_redis_client()
    try:
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await client.delete(*keys)
        return 0
    except RedisError as e:
        print(f"Redis clear pattern error: {e}")
        return 0
