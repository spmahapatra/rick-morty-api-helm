"""Cache backend implementations"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
import json
import redis
import time
import logging

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Store value in cache with TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    def flush(self) -> bool:
        """Clear all cache"""
        pass
    
    @abstractmethod
    def ping(self) -> bool:
        """Test cache connectivity"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class RedisBackend(CacheBackend):
    """Redis cache backend implementation"""
    
    def __init__(self, url: str, pool_size: int = 10, socket_timeout: int = 5):
        """Initialize Redis backend"""
        self.url = url
        self.pool_size = pool_size
        self.socket_timeout = socket_timeout
        self._stats = {"hits": 0, "misses": 0, "errors": 0}
        
        try:
            self.pool = redis.ConnectionPool.from_url(
                url,
                max_connections=pool_size,
                socket_timeout=socket_timeout,
                decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.pool)
            # Test connection
            self.client.ping()
            logger.info(f"Redis connected: {url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from Redis"""
        if not self.client:
            self._stats["errors"] += 1
            return default
        
        try:
            value = self.client.get(key)
            if value is not None:
                self._stats["hits"] += 1
                return json.loads(value)
            else:
                self._stats["misses"] += 1
                return default
        except (redis.RedisError, json.JSONDecodeError, Exception) as e:
            logger.warning(f"Cache get failed for key={key}: {e}")
            self._stats["errors"] += 1
            return default
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Store value in Redis with TTL"""
        if not self.client:
            self._stats["errors"] += 1
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl_seconds, serialized)
            return True
        except (redis.RedisError, json.JSONEncodeError, Exception) as e:
            logger.warning(f"Cache set failed for key={key}, ttl={ttl_seconds}: {e}")
            self._stats["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.warning(f"Cache delete failed for key={key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.warning(f"Cache exists check failed for key={key}: {e}")
            return False
    
    def flush(self) -> bool:
        """Clear all Redis cache"""
        if not self.client:
            return False
        
        try:
            self.client.flushdb()
            self._stats = {"hits": 0, "misses": 0, "errors": 0}
            return True
        except redis.RedisError as e:
            logger.warning(f"Cache flush failed: {e}")
            return False
    
    def ping(self) -> bool:
        """Test Redis connectivity"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.ping())
        except redis.RedisError as e:
            logger.warning(f"Cache ping failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_ratio = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "backend": "redis",
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "total": total,
            "hit_ratio": round(hit_ratio, 2),
            "connected": self.ping()
        }


class InMemoryBackend(CacheBackend):
    """In-memory cache backend for development"""
    
    def __init__(self):
        """Initialize in-memory backend"""
        self.cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)
        self._stats = {"hits": 0, "misses": 0, "errors": 0}
        logger.info("In-memory cache initialized")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from in-memory cache"""
        try:
            if key in self.cache:
                value, expiry_time = self.cache[key]
                if expiry_time > time.time():
                    self._stats["hits"] += 1
                    return value
                else:
                    # Expired
                    del self.cache[key]
                    self._stats["misses"] += 1
                    return default
            else:
                self._stats["misses"] += 1
                return default
        except Exception as e:
            logger.warning(f"Cache get failed for key={key}: {e}")
            self._stats["errors"] += 1
            return default
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Store value in in-memory cache with TTL"""
        try:
            expiry_time = time.time() + ttl_seconds
            self.cache[key] = (value, expiry_time)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key={key}: {e}")
            self._stats["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from in-memory cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory cache"""
        if key not in self.cache:
            return False
        
        value, expiry_time = self.cache[key]
        if expiry_time > time.time():
            return True
        else:
            del self.cache[key]
            return False
    
    def flush(self) -> bool:
        """Clear all in-memory cache"""
        self.cache.clear()
        self._stats = {"hits": 0, "misses": 0, "errors": 0}
        return True
    
    def ping(self) -> bool:
        """Test in-memory cache (always available)"""
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get in-memory cache statistics"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_ratio = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        # Clean up expired entries
        now = time.time()
        expired_count = sum(1 for _, (_, exp) in self.cache.items() if exp <= now)
        
        return {
            "backend": "in-memory",
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "total": total,
            "hit_ratio": round(hit_ratio, 2),
            "connected": True,
            "size": len(self.cache),
            "expired_entries": expired_count
        }
