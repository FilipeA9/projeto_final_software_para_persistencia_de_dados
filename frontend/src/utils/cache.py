"""
Frontend Caching Utilities - Simple caching for API responses.

Provides TTL-based caching for frequently accessed data.
"""

import streamlit as st
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self):
        """Initialize cache storage."""
        if "cache_data" not in st.session_state:
            st.session_state.cache_data = {}
        if "cache_timestamps" not in st.session_state:
            st.session_state.cache_timestamps = {}
    
    def get(self, key: str, ttl_seconds: int = 60) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds
            
        Returns:
            Cached value or None if expired/not found
        """
        if key not in st.session_state.cache_data:
            return None
        
        timestamp = st.session_state.cache_timestamps.get(key)
        if timestamp is None:
            return None
        
        # Check if expired
        now = datetime.now()
        if (now - timestamp).total_seconds() > ttl_seconds:
            # Remove expired entry
            del st.session_state.cache_data[key]
            del st.session_state.cache_timestamps[key]
            return None
        
        return st.session_state.cache_data[key]
    
    def set(self, key: str, value: Any):
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        st.session_state.cache_data[key] = value
        st.session_state.cache_timestamps[key] = datetime.now()
    
    def invalidate(self, key: str):
        """
        Invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        if key in st.session_state.cache_data:
            del st.session_state.cache_data[key]
        if key in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[key]
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (substring)
        """
        keys_to_remove = [
            key for key in st.session_state.cache_data.keys()
            if pattern in key
        ]
        
        for key in keys_to_remove:
            self.invalidate(key)
    
    def clear(self):
        """Clear all cache entries."""
        st.session_state.cache_data = {}
        st.session_state.cache_timestamps = {}


# Global cache instance
cache = SimpleCache()


def cached_api_call(key: str, ttl_seconds: int = 60):
    """
    Decorator for caching API calls.
    
    Args:
        key: Base cache key
        ttl_seconds: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key, ttl_seconds)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_for_spot(spot_id: int):
    """
    Invalidate all cache entries related to a spot.
    
    Args:
        spot_id: ID of the spot
    """
    cache.invalidate_pattern(f"spot_{spot_id}")
    cache.invalidate_pattern("spots_list")


def invalidate_cache_for_user(user_id: int):
    """
    Invalidate all cache entries related to a user.
    
    Args:
        user_id: ID of the user
    """
    cache.invalidate_pattern(f"user_{user_id}")
