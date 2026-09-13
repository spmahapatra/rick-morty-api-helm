"""Tests for cache layer"""

import pytest
import json
import time
from src.cache import RedisBackend, InMemoryBackend, cached


class TestInMemoryBackend:
    """Test in-memory cache backend"""
    
    def test_initialization(self):
        """Test backend initialization"""
        backend = InMemoryBackend()
        assert backend.ping() is True
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        backend = InMemoryBackend()
        backend.set("test_key", {"data": "value"}, ttl_seconds=300)
        result = backend.get("test_key")
        assert result == {"data": "value"}
    
    def test_get_missing_key(self):
        """Test getting non-existent key"""
        backend = InMemoryBackend()
        result = backend.get("missing_key", default="default_value")
        assert result == "default_value"
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        backend = InMemoryBackend()
        backend.set("expire_key", {"data": "value"}, ttl_seconds=1)
        assert backend.get("expire_key") == {"data": "value"}
        time.sleep(1.1)
        assert backend.get("expire_key", default=None) is None
    
    def test_delete(self):
        """Test key deletion"""
        backend = InMemoryBackend()
        backend.set("delete_key", {"data": "value"})
        assert backend.delete("delete_key") is True
        assert backend.get("delete_key", default=None) is None
    
    def test_exists(self):
        """Test key existence check"""
        backend = InMemoryBackend()
        backend.set("exists_key", {"data": "value"})
        assert backend.exists("exists_key") is True
        assert backend.exists("nonexistent_key") is False
    
    def test_flush(self):
        """Test cache flush"""
        backend = InMemoryBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        assert backend.flush() is True
        assert backend.get("key1", default=None) is None
        assert backend.get("key2", default=None) is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        backend = InMemoryBackend()
        backend.set("key1", "value1")
        backend.get("key1")  # hit
        backend.get("key1")  # hit
        backend.get("missing")  # miss
        
        stats = backend.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["backend"] == "in-memory"
        assert stats["hit_ratio"] > 0
    
    def test_store_complex_data(self):
        """Test storing complex data structures"""
        backend = InMemoryBackend()
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "metadata": {
                "total": 2,
                "version": "1.0"
            }
        }
        backend.set("complex", complex_data)
        result = backend.get("complex")
        assert result == complex_data


class TestRedisBackendMock:
    """Test Redis backend with mock"""
    
    def test_redis_backend_initialization_failure(self):
        """Test handling of Redis connection failure"""
        # Use invalid URL to trigger connection error
        backend = RedisBackend("redis://invalid:1234/0")
        assert backend.client is None
    
    def test_redis_backend_graceful_degradation(self):
        """Test graceful degradation when Redis is unavailable"""
        backend = RedisBackend("redis://invalid:1234/0")
        
        # All operations should return gracefully
        assert backend.get("key") is None
        assert backend.set("key", "value") is False
        assert backend.delete("key") is False
        assert backend.ping() is False


class TestCacheDecorator:
    """Test cache decorator"""
    
    def test_decorator_basic(self):
        """Test basic decorator functionality"""
        backend = InMemoryBackend()
        call_count = 0
        
        @cached(ttl_seconds=300)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": "expensive"}
        
        # First call should execute function
        result1 = expensive_function(backend)
        assert result1 == {"result": "expensive"}
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(backend)
        assert result2 == {"result": "expensive"}
        assert call_count == 1  # Function not called again
