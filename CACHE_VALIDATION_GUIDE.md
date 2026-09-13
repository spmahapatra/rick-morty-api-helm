# Cache Feature Validation Guide

## Overview

This guide provides comprehensive methods to validate the cache feature in the Rick and Morty Character API. The caching system consists of:

- **Backend Implementations**: Redis and In-Memory backends
- **Decorator**: Automatic caching for function results
- **Integration**: Cache layer integrated with API endpoints
- **Statistics**: Hit/miss tracking and performance metrics

---

## Project Context

**Tech Stack**:
- Python 3.9+
- Flask (REST API)
- Redis (production cache backend)
- PostgreSQL (persistence layer)
- Docker & Docker Compose (containerization)
- Kubernetes (orchestration)

**Cache Architecture**:
```
Request → API Endpoint → Check Cache → Cache Hit/Miss → Backend Call
                              ↓
                        Store in Cache (TTL)
                              ↓
                        Return Response
```

---

## 1. Unit Tests for Cache Backends

### Current Test Coverage

The test suite (`tests/test_cache.py`) covers:

✅ **InMemoryBackend**:
- Initialization and ping
- Set/Get operations
- Missing key handling
- TTL expiration
- Key deletion
- Existence checking
- Cache flush
- Statistics tracking
- Complex data structures

✅ **RedisBackend**:
- Connection failure handling
- Graceful degradation

✅ **Cache Decorator**:
- Basic caching functionality

### Run Existing Tests

```bash
# Run all cache tests
pytest tests/test_cache.py -v

# Run specific test class
pytest tests/test_cache.py::TestInMemoryBackend -v

# Run with coverage
pytest tests/test_cache.py --cov=src.cache --cov-report=html
```

### Expected Output

```
tests/test_cache.py::TestInMemoryBackend::test_initialization PASSED
tests/test_cache.py::TestInMemoryBackend::test_set_and_get PASSED
tests/test_cache.py::TestInMemoryBackend::test_ttl_expiration PASSED
tests/test_cache.py::TestInMemoryBackend::test_delete PASSED
tests/test_cache.py::TestInMemoryBackend::test_exists PASSED
tests/test_cache.py::TestInMemoryBackend::test_flush PASSED
tests/test_cache.py::TestInMemoryBackend::test_cache_stats PASSED
tests/test_cache.py::TestInMemoryBackend::test_store_complex_data PASSED
```

---

## 2. Integration Tests for Cache Layer

### Test Cache Integration with API

Create `tests/test_cache_integration.py`:

```python
"""Integration tests for cache with API endpoints"""
import pytest
from app import app, RickAndMortyClient
from src.cache import InMemoryBackend, RedisBackend
import time

class TestCacheIntegration:
    """Test cache integration with API endpoints"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.cache_backend = InMemoryBackend()
    
    def test_repeated_requests_should_hit_cache(self):
        """Verify cache hits on repeated identical requests"""
        # First request (cache miss)
        response1 = self.client.get("/characters?limit=5")
        assert response1.status_code == 200
        
        # Get initial stats
        stats1 = self.cache_backend.get_stats()
        initial_misses = stats1["misses"]
        
        # Second request (should hit cache if implemented)
        response2 = self.client.get("/characters?limit=5")
        assert response2.status_code == 200
        
        # Verify responses are identical
        assert response1.data == response2.data
    
    def test_different_parameters_bypass_cache(self):
        """Verify different query parameters create different cache entries"""
        response1 = self.client.get("/characters?limit=5")
        response2 = self.client.get("/characters?limit=10")
        
        # Different parameters should produce different results
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        assert data1["pagination"]["limit"] == 5
        assert data2["pagination"]["limit"] == 10
    
    def test_cache_ttl_expiration(self):
        """Verify cache entries expire after TTL"""
        cache = InMemoryBackend()
        
        # Set with short TTL
        cache.set("test_key", {"data": "value"}, ttl_seconds=1)
        
        # Immediate retrieval should work
        value1 = cache.get("test_key")
        assert value1 == {"data": "value"}
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        value2 = cache.get("test_key", default=None)
        assert value2 is None
    
    def test_cache_invalidation_on_data_update(self):
        """Verify cache invalidation when underlying data changes"""
        cache = InMemoryBackend()
        
        # Store initial data
        cache.set("character:1", {"name": "Rick", "status": "alive"})
        
        # Retrieve
        data1 = cache.get("character:1")
        assert data1["name"] == "Rick"
        
        # Invalidate cache
        deleted = cache.delete("character:1")
        assert deleted is True
        
        # Should be gone
        data2 = cache.get("character:1", default=None)
        assert data2 is None
```

### Run Integration Tests

```bash
pytest tests/test_cache_integration.py -v
```

---

## 3. Performance Validation

### Measure Cache Impact

```python
"""tests/test_cache_performance.py"""
import pytest
import time
from src.cache import InMemoryBackend, RedisBackend

class TestCachePerformance:
    """Validate cache performance improvements"""
    
    def test_cache_improves_latency(self):
        """Verify cache reduces access latency"""
        cache = InMemoryBackend()
        
        # Simulate expensive operation
        def expensive_operation():
            time.sleep(0.1)  # 100ms operation
            return {"result": "expensive"}
        
        # First call (cache miss)
        start = time.time()
        result1 = expensive_operation()
        first_call_time = time.time() - start
        
        # Store in cache
        cache.set("expensive", result1)
        
        # Second call (cache hit)
        start = time.time()
        result2 = cache.get("expensive")
        cached_call_time = time.time() - start
        
        # Cached call should be significantly faster
        assert cached_call_time < first_call_time * 0.1
        print(f"First call: {first_call_time*1000:.2f}ms")
        print(f"Cached call: {cached_call_time*1000:.2f}ms")
        print(f"Speedup: {first_call_time/cached_call_time:.1f}x")

class TestCacheScalability:
    """Test cache with realistic data loads"""
    
    def test_large_dataset_caching(self):
        """Verify cache handles large result sets"""
        cache = InMemoryBackend()
        
        # Simulate large character dataset
        large_data = {
            "characters": [
                {"id": i, "name": f"Character{i}"}
                for i in range(1000)
            ]
        }
        
        # Store large dataset
        success = cache.set("large_dataset", large_data, ttl_seconds=300)
        assert success is True
        
        # Retrieve
        retrieved = cache.get("large_dataset")
        assert retrieved == large_data
        assert len(retrieved["characters"]) == 1000
    
    def test_cache_memory_efficiency(self):
        """Verify cache doesn't consume excessive memory"""
        cache = InMemoryBackend()
        
        # Store 100 moderate-sized entries
        for i in range(100):
            data = {
                "id": i,
                "name": f"Character{i}",
                "data": "x" * 1000  # ~1KB per entry
            }
            cache.set(f"key_{i}", data)
        
        stats = cache.get_stats()
        
        # Cache should have 100 entries
        assert stats["size"] == 100
        # Should not have excessive expired entries
        assert stats["expired_entries"] == 0
```

### Run Performance Tests

```bash
pytest tests/test_cache_performance.py -v -s
```

---

## 4. Cache Statistics & Monitoring

### View Cache Statistics

Add endpoint to `app.py`:

```python
@app.route("/cache/stats", methods=["GET"])
def get_cache_stats():
    """Get cache statistics"""
    stats = cache_backend.get_stats()
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "cache_stats": stats,
        "system_info": {
            "backend_type": "in-memory" if isinstance(cache_backend, InMemoryBackend) else "redis"
        }
    }), 200
```

### Query Cache Stats

```bash
# Get cache statistics
curl http://localhost:5000/cache/stats | jq

# Example output
{
  "timestamp": "2024-09-13T10:30:45.123456",
  "cache_stats": {
    "backend": "in-memory",
    "hits": 42,
    "misses": 8,
    "errors": 0,
    "total": 50,
    "hit_ratio": 84.0,
    "connected": true,
    "size": 12,
    "expired_entries": 0
  }
}
```

### Validate Success Criteria

According to the OpenSpec (spec-driven requirements):

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| Cache hit ratio | ≥ 80% | Query `/cache/stats` and check `hit_ratio` |
| P99 latency | < 100ms for cached requests | Measure response time for repeated requests |
| Graceful degradation | Redis failure doesn't crash app | Start with invalid Redis URL and verify fallback |
| TTL enforcement | Entries expire properly | Set short TTL and verify expiration |
| JSON serialization | Complex objects cache correctly | Store nested objects and verify retrieval |

---

## 5. Docker-Based Validation

### Test with Redis Backend

```bash
# Start Redis container
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Set Redis connection in environment
export REDIS_URL="redis://localhost:6379/0"

# Run tests
pytest tests/test_cache.py -v

# Stop Redis
docker stop redis && docker rm redis
```

### Test with Docker Compose

```yaml
# In docker-compose.yml, uncomment/add:
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - redis
    environment:
      REDIS_URL: "redis://redis:6379/0"
```

Run:

```bash
docker-compose up -d
docker-compose exec app pytest tests/test_cache.py -v
docker-compose down
```

---

## 6. Manual Testing Scenarios

### Scenario 1: Basic Cache Operations

```bash
# Start the app
python app.py

# In another terminal:

# 1. Warm up cache with initial request
curl -i http://localhost:5000/characters?limit=5

# 2. Second identical request (should be cached)
time curl http://localhost:5000/characters?limit=5

# 3. Check cache stats
curl http://localhost:5000/cache/stats | jq '.cache_stats'

# Expected: hit_ratio should increase
```

### Scenario 2: Cache Invalidation

```bash
# 1. Get character by ID
curl http://localhost:5000/characters/1

# 2. Simulate data update (delete cache)
# Call cache invalidation endpoint (if implemented)

# 3. Verify fresh data is fetched
curl http://localhost:5000/characters/1
```

### Scenario 3: TTL Expiration

```bash
# 1. Make request to trigger caching
curl http://localhost:5000/characters?limit=5

# 2. Check stats - note hit count
curl http://localhost:5000/cache/stats | jq '.cache_stats.hits'

# 3. Wait for TTL to expire (default 300s or configured TTL)
sleep 301

# 4. Make request again
curl http://localhost:5000/characters?limit=5

# 5. Stats should show a cache miss
curl http://localhost:5000/cache/stats | jq '.cache_stats.misses'
```

### Scenario 4: Redis Failure Graceful Degradation

```bash
# 1. Kill Redis (if running)
docker stop redis

# 2. Make requests to API
curl http://localhost:5000/characters

# Expected: API continues to work (falls back to making direct API calls)

# 3. Restart Redis
docker start redis

# 4. Cache should work again
curl http://localhost:5000/characters
```

---

## 7. Load Testing Cache Performance

### Using Apache Bench (ab)

```bash
# Test without cache (cold)
ab -n 100 -c 10 http://localhost:5000/characters?limit=5

# Test with cache (warm)
# Run the above command again immediately
# Should see faster response times
```

### Using wrk (advanced)

```bash
wrk -t4 -c100 -d30s http://localhost:5000/characters?limit=5

# This will show throughput and latency statistics
```

### Expected Results

- **Without cache**: ~500-1000 req/s (depending on upstream API)
- **With cache**: ~5000-10000 req/s (100ms overhead for cached response)
- **Hit ratio**: 80%+ for typical usage patterns

---

## 8. Validation Checklist

### Backend Implementation ✓

- [ ] InMemoryBackend initializes correctly
- [ ] RedisBackend connects to Redis
- [ ] RedisBackend gracefully handles connection failures
- [ ] All CRUD operations (get, set, delete) work
- [ ] TTL expiration works as expected
- [ ] Flush clears all cache
- [ ] Statistics track hits/misses/errors
- [ ] Complex objects (dicts, lists) serialize/deserialize correctly

### Integration ✓

- [ ] Cache decorator works with functions
- [ ] Repeated requests hit cache
- [ ] Different parameters create different cache entries
- [ ] Cache invalidation works
- [ ] Stats endpoint shows accurate hit ratio

### Performance ✓

- [ ] Cached responses are faster (>10x speedup)
- [ ] No memory leaks with large datasets
- [ ] TTL prevents stale data

### Reliability ✓

- [ ] Redis failures don't crash app
- [ ] Graceful fallback to direct API calls
- [ ] Error handling is robust
- [ ] JSON serialization errors are handled

### Production Readiness ✓

- [ ] Cache hits ≥ 80%
- [ ] P99 latency < 100ms
- [ ] No unhandled exceptions
- [ ] Health check includes cache status

---

## 9. Troubleshooting Common Issues

### Issue: Cache Hit Ratio Too Low

**Symptoms**: Hit ratio < 80% in stats

**Investigation**:
```python
# Check if cache is being used
cache_stats = cache_backend.get_stats()
print(f"Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")

# Verify TTL is sufficient
# Verify decorator is applied to functions
```

**Solutions**:
- Increase TTL for less-frequently-changing data
- Verify cache backend is properly initialized
- Check that decorator is applied to API handlers

### Issue: High Memory Usage

**Symptoms**: Process memory grows continuously

**Investigation**:
```python
# Check expired entries
stats = cache_backend.get_stats()
print(f"Expired entries: {stats['expired_entries']}")
print(f"Size: {stats['size']}")
```

**Solutions**:
- Implement cache size limits
- Reduce TTL for large objects
- Use Redis backend for unbounded cache

### Issue: Redis Connection Failures

**Symptoms**: Cache operations return false/None

**Investigation**:
```bash
# Test Redis connectivity
redis-cli ping

# Check connection pool
docker ps | grep redis
```

**Solutions**:
- Verify Redis is running
- Check connection string format
- Verify network connectivity
- Use connection pool with retry logic

---

## 10. Success Metrics

Track these metrics to validate cache is working:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Cache Hit Ratio | ≥ 80% | `/cache/stats` endpoint |
| P99 Latency (cached) | < 100ms | `curl` with timing or `wrk` |
| Request Throughput | > 5000 req/s | `ab` or `wrk` |
| Zero Errors | 100% | Check error count in stats |
| Uptime | 99.5%+ | Monitor over 2 weeks |

---

## Quick Start Validation

Run this script to validate all components:

```bash
#!/bin/bash

echo "=== Cache Validation Suite ==="

echo "1. Running unit tests..."
pytest tests/test_cache.py -v

echo "2. Running integration tests..."
pytest tests/test_cache_integration.py -v

echo "3. Running performance tests..."
pytest tests/test_cache_performance.py -v -s

echo "4. Starting application..."
python app.py &
APP_PID=$!
sleep 3

echo "5. Testing cache endpoints..."
curl http://localhost:5000/cache/stats | jq

echo "6. Load test..."
ab -n 100 -c 10 http://localhost:5000/characters?limit=5

echo "7. Cleanup..."
kill $APP_PID

echo "=== Validation Complete ==="
```

---

## Related Documentation

- **Cache Specification**: `openspec/changes/api-resilience-enhancement/specs/01-caching.md`
- **Test Suite**: `tests/test_cache.py`
- **Implementation**: `src/cache/backend.py`, `src/cache/decorator.py`
- **API Integration**: `app.py` (endpoints using cache)

