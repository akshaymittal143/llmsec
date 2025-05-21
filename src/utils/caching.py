from typing import Any, Callable, Dict, Optional
import time
import functools
import hashlib
import json
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

class Cache:
    """Simple in-memory cache with TTL."""
    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
            
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with expiry."""
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cached values."""
        self._cache.clear()

# Global cache instance
_cache = Cache()

def cache_result(ttl_seconds: int = 3600):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time-to-live in seconds for cached results
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function args
            key_dict = {
                'func': func.__name__,
                'args': [str(arg) for arg in args],
                'kwargs': {k: str(v) for k, v in kwargs.items()}
            }
            key = hashlib.sha256(
                json.dumps(key_dict, sort_keys=True).encode()
            ).hexdigest()
            
            # Check cache
            cached = _cache.get(key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            
            # Handle dataclass results
            if hasattr(result, '__dataclass_fields__'):
                cache_value = asdict(result)
            else:
                cache_value = result
                
            _cache.set(key, cache_value, ttl_seconds)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator