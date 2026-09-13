"""Cache decorator for automatic caching"""

from functools import wraps
from typing import Optional, Callable, Any
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cached(ttl_seconds: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(cache_backend, *args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key_str = "|".join(key_parts)
                cache_key = f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_value = cache_backend.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Store in cache
            ttl = ttl_seconds or 300
            cache_backend.set(cache_key, result, ttl_seconds=ttl)
            logger.debug(f"Cached result for {cache_key} with TTL={ttl}s")
            
            return result
        
        return wrapper
    
    return decorator
