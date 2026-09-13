"""Rate limiting implementation"""

import time
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, retry_after_s: int, remaining: int = 0):
        self.retry_after_s = retry_after_s
        self.remaining = remaining
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_s}s")


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, limit_per_minute: int = 100):
        """Initialize rate limiter"""
        self.limit_per_minute = limit_per_minute
        # Use in-memory storage: key -> (count, reset_time)
        self.counters: Dict[str, Tuple[int, float]] = {}
    
    def check_rate_limit(self, consumer_id: str) -> Dict[str, any]:
        """Check if consumer has exceeded rate limit"""
        current_time = time.time()
        current_minute = int(current_time // 60) * 60
        reset_time = (int(current_time // 60) + 1) * 60
        
        key = f"rate_limit:{consumer_id}:{current_minute}"
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        if key in self.counters:
            count, expiry = self.counters[key]
            if expiry > current_time:
                # Still in same minute window
                count += 1
            else:
                # New minute window
                count = 1
                expiry = reset_time
        else:
            count = 1
            expiry = reset_time
        
        self.counters[key] = (count, expiry)
        
        allowed = count <= self.limit_per_minute
        remaining = max(0, self.limit_per_minute - count)
        
        return {
            'allowed': allowed,
            'count': count,
            'limit': self.limit_per_minute,
            'remaining': remaining,
            'reset_time': int(reset_time),
            'retry_after_s': 0 if allowed else int(reset_time - current_time) + 1
        }
    
    def is_rate_limited(self, consumer_id: str) -> bool:
        """Check if consumer is rate limited"""
        result = self.check_rate_limit(consumer_id)
        return not result['allowed']
    
    def get_retry_after(self, consumer_id: str) -> int:
        """Get seconds to wait before next request"""
        result = self.check_rate_limit(consumer_id)
        return result['retry_after_s']
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove expired entries from counters"""
        expired_keys = [
            key for key, (_, expiry) in self.counters.items()
            if expiry < current_time
        ]
        for key in expired_keys:
            del self.counters[key]
    
    def reset(self, consumer_id: str) -> None:
        """Reset rate limit for consumer"""
        keys_to_delete = [
            key for key in self.counters.keys()
            if key.startswith(f"rate_limit:{consumer_id}:")
        ]
        for key in keys_to_delete:
            del self.counters[key]
        logger.info(f"Rate limit reset for consumer {consumer_id}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics"""
        return {
            "limit_per_minute": self.limit_per_minute,
            "active_consumers": len(set(
                key.split(":")[1] for key in self.counters.keys()
            )),
            "tracked_entries": len(self.counters)
        }


class RedisRateLimiter:
    """Redis-backed rate limiter (when Redis is available)"""
    
    def __init__(self, cache_backend, limit_per_minute: int = 100):
        """Initialize Redis rate limiter"""
        self.cache_backend = cache_backend
        self.limit_per_minute = limit_per_minute
    
    def check_rate_limit(self, consumer_id: str) -> Dict[str, any]:
        """Check rate limit using Redis"""
        try:
            current_time = time.time()
            current_minute = int(current_time // 60)
            reset_time = (current_minute + 1) * 60
            
            # This is a simplified version without true Redis INCR support
            # In production, use redis.incr() for atomic operations
            key = f"rate_limit:{consumer_id}:{current_minute}"
            
            count = self.cache_backend.get(key, 0)
            count += 1
            self.cache_backend.set(key, count, ttl_seconds=61)
            
            allowed = count <= self.limit_per_minute
            remaining = max(0, self.limit_per_minute - count)
            
            return {
                'allowed': allowed,
                'count': count,
                'limit': self.limit_per_minute,
                'remaining': remaining,
                'reset_time': int(reset_time),
                'retry_after_s': 0 if allowed else int(reset_time - current_time) + 1
            }
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fall back to allowing the request
            return {
                'allowed': True,
                'count': 0,
                'limit': self.limit_per_minute,
                'remaining': self.limit_per_minute,
                'reset_time': int(time.time() + 60),
                'retry_after_s': 0
            }
    
    def is_rate_limited(self, consumer_id: str) -> bool:
        """Check if consumer is rate limited"""
        result = self.check_rate_limit(consumer_id)
        return not result['allowed']
