# Cache Hit/Miss Detection & Verification Guide

**Date**: 2026-09-13  
**Status**: Complete Implementation Strategy  
**Purpose**: Technical explanation and implementation for distinguishing cached vs. origin responses

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Fundamentals](#fundamentals)
3. [Detection Methods](#detection-methods)
4. [Implementation Strategy](#implementation-strategy)
5. [Response Headers](#response-headers)
6. [Logging & Monitoring](#logging--monitoring)
7. [Code Examples](#code-examples)
8. [Verification Techniques](#verification-techniques)
9. [Advanced Topics](#advanced-topics)
10. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### What is Cache Hit/Miss Detection?

Cache hit/miss detection is the ability to identify whether a response:
- **Cache Hit**: Came from Redis cache (fast, no upstream processing)
- **Cache Miss**: Was generated from origin source (slow, fresh data)
- **Bypass**: Deliberately skipped cache (bypass headers, uncacheable)

### Why It Matters

Understanding cache behavior is critical for:
- **Performance Optimization**: Identify which requests are fast (cached) vs slow (misses)
- **Debugging**: Determine if stale data is being served
- **Monitoring**: Track cache effectiveness and hit ratio
- **Cost Analysis**: Cached requests save API calls to Rick and Morty API
- **User Experience**: Identify slow endpoints that need better caching

### Current Implementation Status

The project already has:
- ✅ Redis backend with hit/miss tracking (see `src/cache/backend.py:60`)
- ✅ In-memory cache for development
- ✅ Structured JSON logging throughout
- ✅ Correlation ID tracking per request

**What's Missing**:
- Response headers indicating cache status
- Per-request cache detection middleware
- Cache hit/miss logging in API responses
- Monitoring dashboard/metrics
- Client-facing cache status indicators

---

## Fundamentals

### Cache Hit/Miss Lifecycle

```
Request arrives
  ↓
1. Check cache with generated key
  ├─ Cache HIT: Return cached value
  │  ├─ Mark: cache_status = "HIT"
  │  ├─ Log: "Cache hit for key=X"
  │  └─ Header: X-Cache: hit
  ↓
  └─ Cache MISS: Key not in cache
     ├─ Mark: cache_status = "MISS"
     ├─ Fetch: Call origin (Rick and Morty API)
     ├─ Store: Save to cache with TTL
     ├─ Log: "Cache miss for key=X, stored with TTL=300s"
     └─ Header: X-Cache: miss
  ↓
2. Return response
```

### Cache Key Generation

**Current approach** (from `src/cache/decorator.py:19-27`):

```python
# Using custom key function (if provided)
cache_key = key_func(*args, **kwargs)

# Or default: hash function name + args
key_str = "function_name|arg1|arg2|kwarg1=val1|kwarg2=val2"
cache_key = f"cache:{md5(key_str).hexdigest()}"
```

**For API endpoints**, keys should be:
```
Format: cache:endpoint:method:params
Example: cache:characters:get:page=1&limit=10
```

---

## Detection Methods

### Method 1: Response Headers (Client-Side)

**Most Accessible**: Client can see cache status without parsing response body

```
Request:
  GET /characters?page=1&limit=10
  
Response Headers:
  X-Cache: hit                    # or 'miss' or 'bypass'
  X-Cache-Key: cache:characters:get:params_hash
  X-Cache-Age: 45                # seconds cached
  X-Cache-TTL: 300               # seconds until expiry
  X-Cache-Hit-Ratio: 75.5         # backend cache stats
```

### Method 2: Response Body Metadata

**Most Flexible**: Include cache info in JSON response

```json
{
  "data": [...],
  "pagination": {...},
  "_cache": {
    "status": "hit",
    "key": "cache:characters:get:1_10",
    "age_seconds": 45,
    "ttl_seconds": 300,
    "stored_at": "2026-09-13T02:20:15Z"
  }
}
```

### Method 3: Structured Logging

**Best for Monitoring**: Log every cache operation with context

```json
{
  "timestamp": "2026-09-13T02:25:10Z",
  "message": "API response",
  "level": "INFO",
  "cache_status": "hit",
  "cache_key": "cache:characters:get:1_10",
  "cache_age_seconds": 45,
  "endpoint": "/characters",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 2.5,
  "correlation_id": "abc-123"
}
```

### Method 4: Custom HTTP Headers

**RFC 7234 Compliant**: Use standard cache headers

```
Cache-Control: public, max-age=300              # HTTP standard
ETag: "abc123xyz"                               # Content hash
Last-Modified: Thu, 13 Sep 2026 02:20:15 GMT   # When cached
Age: 45                                         # Seconds cached
X-Cache-Status: hit                             # Custom cache indicator
```

### Method 5: Query Parameter Override

**Debugging Tool**: Allow clients to bypass cache for testing

```
Request:
  GET /characters?page=1&cache=bypass
  
Behavior:
  • Ignores cache (always MISS)
  • Fetches fresh from origin
  • Response header: X-Cache: bypass
  
Request:
  GET /characters?page=1&cache=stats
  
Behavior:
  • Returns cache stats
  • No data fetch
  • Useful for monitoring
```

---

## Implementation Strategy

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Request                         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Cache Detection Middleware                    │
│  1. Extract cache key from request                       │
│  2. Check Redis for cached response                      │
│  3. Set cache_status in request context                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
              HIT?    │    MISS?
              ↙       │       ↖
           YES        │        NO
            ↓         │         ↓
        Return    ┌───┴───┐  Fetch Origin
        Cached    │       │  Store in Cache
        Response  │       │
                  ↓       ↓
        ┌─────────────────────────────┐
        │  Add Cache Headers/Metadata  │
        │  Log Cache Status            │
        │  Return Response             │
        └─────────────────────────────┘
```

### Three-Layer Implementation

#### Layer 1: Middleware (Cache Detection)

Detects cache status before endpoint is called:

```python
@app.before_request
def detect_cache_status():
    # Generate cache key from request
    cache_key = generate_cache_key(request)
    
    # Check if in cache
    cached_value = cache_backend.get(cache_key)
    
    # Store in request context
    g.cache_key = cache_key
    g.cache_status = "HIT" if cached_value else "MISS"
    g.cache_data = cached_value if cached_value else None
```

#### Layer 2: Endpoint Handler (Use Cached Data)

Uses cache_status to decide response path:

```python
@app.route("/characters")
def get_characters():
    cache_status = g.cache_status
    
    if cache_status == "HIT":
        data = g.cache_data
        response = jsonify(data)
    else:
        # Fetch from origin
        data = fetch_from_origin()
        cache_backend.set(cache_key, data, ttl=300)
        response = jsonify(data)
    
    # Add headers
    response.headers["X-Cache"] = cache_status.lower()
    return response
```

#### Layer 3: Response Processing (Headers & Logging)

Adds metadata and logs cache information:

```python
@app.after_request
def add_cache_headers(response):
    cache_status = g.get("cache_status", "UNKNOWN")
    cache_key = g.get("cache_key", "")
    
    # Add standard headers
    response.headers["X-Cache"] = cache_status.lower()
    response.headers["X-Cache-Key"] = cache_key
    
    # Log cache operation
    logger.info(
        "Response sent",
        cache_status=cache_status,
        cache_key=cache_key,
        response_time_ms=elapsed_time,
        status_code=response.status_code
    )
    
    return response
```

---

## Response Headers

### Recommended Header Set

| Header | Purpose | Example | Standard? |
|--------|---------|---------|-----------|
| `X-Cache` | Cache status (hit/miss/bypass) | `hit` | Custom |
| `X-Cache-Key` | Generated cache key | `cache:characters:get:hash` | Custom |
| `X-Cache-Age` | Seconds since cached | `45` | Custom |
| `X-Cache-TTL` | Seconds until expiry | `255` | Custom |
| `Age` | RFC 7234 age header | `45` | Standard |
| `Cache-Control` | Browser caching directive | `public, max-age=300` | Standard |
| `ETag` | Content hash for validation | `"abc123"` | Standard |
| `Last-Modified` | RFC 7234 modification time | `Thu, 13 Sep 2026 02:20:15 GMT` | Standard |

### Header Values

#### X-Cache Values

```
X-Cache: hit         # Cache hit - data served from Redis
X-Cache: miss        # Cache miss - fetched from origin
X-Cache: bypass      # Deliberately bypassed cache
X-Cache: error       # Cache backend error, served anyway
X-Cache: conditional # ETag matched, served from cache
```

#### Cache-Control Values

```
Cache-Control: public, max-age=300              # Browser + CDN caching
Cache-Control: private, max-age=300             # Browser only
Cache-Control: no-cache, no-store, must-revalidate  # Never cache
Cache-Control: max-age=300, stale-while-revalidate=60  # Advanced
```

### Complete Header Example

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Cache: hit
X-Cache-Key: cache:characters:get:page=1_limit=10
X-Cache-Age: 45
X-Cache-TTL: 255
Age: 45
Cache-Control: public, max-age=300
ETag: "abc123xyz789def"
Last-Modified: Thu, 13 Sep 2026 02:20:15 GMT
Expires: Thu, 13 Sep 2026 02:25:15 GMT
Vary: Accept-Encoding
Date: Thu, 13 Sep 2026 02:25:10 GMT
Content-Length: 1234

{
  "data": [...],
  "pagination": {...}
}
```

---

## Logging & Monitoring

### Structured Logging Format

Every cache operation should be logged as JSON:

```json
{
  "timestamp": "2026-09-13T02:25:10.123456Z",
  "level": "INFO",
  "logger": "app.cache",
  "message": "Cache operation completed",
  "correlation_id": "req-abc-123-xyz",
  "cache_status": "hit",
  "cache_operation": "get",
  "cache_key": "cache:characters:get:page=1_limit=10",
  "cache_backend": "redis",
  "cache_age_seconds": 45,
  "cache_ttl_seconds": 300,
  "endpoint": "/characters",
  "method": "GET",
  "query_params": {"page": "1", "limit": "10"},
  "response_time_ms": 2.5,
  "status_code": 200
}
```

### Log Levels by Cache Event

```
DEBUG:   cache_key_generated
DEBUG:   cache_lookup_started
DEBUG:   cache_serialization (complex objects)

INFO:    cache_hit (successful retrieval)
INFO:    cache_miss (origin fetch)
INFO:    cache_stored (new entry)

WARNING: cache_stale (expired but served)
WARNING: cache_serialization_error (recovered)
WARNING: cache_key_collision (unlikely but log it)

ERROR:   cache_backend_unavailable (Redis down)
ERROR:   cache_store_failed (write error)
ERROR:   cache_corruption (corrupted data)
```

### Metrics to Track

```python
class CacheMetrics:
    """Track cache performance metrics"""
    
    hits: int                   # Total cache hits
    misses: int                 # Total cache misses
    errors: int                 # Cache backend errors
    hit_ratio: float            # hits / (hits + misses) * 100
    
    avg_cache_response_ms: float    # Average cached request time
    avg_origin_response_ms: float   # Average origin request time
    avg_savings_ms: float           # avg_origin - avg_cache
    
    keys_stored: int            # Number of cached keys
    memory_used_mb: float       # Redis memory usage
    ttl_distribution: Dict      # Number of keys by TTL bucket
```

### Sample Log Output

```json
{
  "timestamp": "2026-09-13T02:25:10.123Z",
  "message": "Response sent",
  "level": "INFO",
  "correlation_id": "req-001",
  "endpoint": "/characters",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 2.5,
  "cache_status": "HIT",
  "cache_key": "cache:characters:get:page=1_limit=10",
  "cache_age_seconds": 45,
  "cache_backend": "redis",
  "hit_ratio": "75.50%"
}
```

---

## Code Examples

### Example 1: Simple Cache Detection Middleware

```python
# Add to app.py or new middleware file

from flask import g, request
import hashlib

def generate_cache_key(req: request) -> str:
    """Generate cache key from request"""
    key_parts = [
        req.endpoint,
        req.method,
    ]
    
    # Add sorted query parameters
    for key, value in sorted(request.args.items()):
        key_parts.append(f"{key}={value}")
    
    key_str = ":".join(key_parts)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"cache:{req.endpoint}:{req.method}:{key_hash}"


@app.before_request
def detect_cache_status():
    """Detect if request is cacheable and cache status"""
    
    # Skip health checks
    if request.endpoint == "health_check":
        g.cache_enabled = False
        return
    
    # Check for cache bypass query parameter
    cache_param = request.args.get("cache", "").lower()
    if cache_param == "bypass":
        g.cache_status = "BYPASS"
        g.cache_enabled = False
        return
    
    # Generate cache key
    cache_key = generate_cache_key(request)
    g.cache_key = cache_key
    
    # Try to get from cache
    try:
        from config import get_cache_backend
        backend = get_cache_backend()
        cached_data = backend.get(cache_key)
        
        if cached_data:
            g.cache_status = "HIT"
            g.cached_data = cached_data
            g.cache_enabled = True
        else:
            g.cache_status = "MISS"
            g.cached_data = None
            g.cache_enabled = True
    except Exception as e:
        logger.warning(
            "Cache detection failed",
            error=str(e),
            cache_key=cache_key
        )
        g.cache_status = "ERROR"
        g.cache_enabled = False
```

### Example 2: Cache-Aware Response Handler

```python
@app.route("/characters", methods=["GET"])
@handle_api_errors
def get_characters():
    """Get characters with cache detection"""
    
    # Check if cached
    cache_status = g.get("cache_status", "UNKNOWN")
    
    if cache_status == "HIT" and g.get("cached_data"):
        # Serve from cache
        data = g.cached_data
        logger.debug(
            "Serving from cache",
            cache_key=g.cache_key,
            cache_status="HIT"
        )
    else:
        # Fetch from origin
        try:
            client = RickAndMortyClient()
            api_response = client.fetch_characters(
                page=1,
                status=FILTERS["status"],
                species=FILTERS["species"]
            )
            
            characters = api_response.get("results", [])
            characters = filter_characters_by_origin(characters)
            characters = sort_characters(characters)
            data, pagination_info = paginate_characters(characters, 1, 10)
            
            # Prepare response data
            data = {
                "data": data,
                "pagination": pagination_info,
                "filters": {...}
            }
            
            # Store in cache
            if g.get("cache_enabled"):
                from config import get_cache_backend
                backend = get_cache_backend()
                backend.set(g.cache_key, data, ttl_seconds=300)
                
        except Exception as e:
            logger.error("Failed to fetch characters", error=str(e))
            raise
    
    response = jsonify(data)
    return response
```

### Example 3: Add Cache Headers

```python
@app.after_request
def add_cache_response_headers(response):
    """Add cache-related headers to response"""
    
    cache_status = g.get("cache_status", "UNKNOWN")
    cache_key = g.get("cache_key", "")
    
    # Add X-Cache header (hit/miss/bypass/error)
    response.headers["X-Cache"] = cache_status.lower()
    
    if cache_key:
        response.headers["X-Cache-Key"] = cache_key
    
    # Add cache age if hit
    if cache_status == "HIT":
        try:
            from config import get_cache_backend
            backend = get_cache_backend()
            stats = backend.get_stats()
            
            # Calculate age (simplified - would need to store in cache)
            response.headers["X-Cache-Age"] = "unknown"
            response.headers["X-Cache-TTL"] = "300"
            response.headers["Age"] = "45"  # In seconds
        except:
            pass
    
    # Add standard cache headers
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["Vary"] = "Accept-Encoding"
    
    return response
```

### Example 4: Cache Statistics Endpoint

```python
@app.route("/api/cache/stats", methods=["GET"])
def get_cache_stats():
    """Get cache statistics"""
    
    try:
        from config import get_cache_backend
        backend = get_cache_backend()
        stats = backend.get_stats()
        
        return jsonify({
            "status": "ok",
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    except Exception as e:
        logger.error("Failed to get cache stats", error=str(e))
        return jsonify({"error": "Failed to get stats"}), 500


@app.route("/api/cache/flush", methods=["POST"])
def flush_cache():
    """Flush cache (admin endpoint)"""
    
    try:
        from config import get_cache_backend
        backend = get_cache_backend()
        
        if backend.flush():
            logger.info("Cache flushed")
            return jsonify({"status": "ok", "message": "Cache flushed"}), 200
        else:
            return jsonify({"error": "Failed to flush cache"}), 500
    except Exception as e:
        logger.error("Cache flush failed", error=str(e))
        return jsonify({"error": "Cache flush failed"}), 500
```

---

## Verification Techniques

### Technique 1: Header Inspection (curl)

```bash
# Request with cache detection
curl -v http://localhost:5000/characters?page=1&limit=10 \
  -H "X-Correlation-ID: test-001"

# Output inspection:
# < X-Cache: hit             (or miss)
# < X-Cache-Key: cache:...
# < Age: 45
```

### Technique 2: Response Time Comparison

```bash
# First request (MISS)
time curl -s http://localhost:5000/characters?page=1 > /dev/null
# Real: 0.850s (origin fetch)

# Second request (HIT)
time curl -s http://localhost:5000/characters?page=1 > /dev/null
# Real: 0.005s (cache serve)

# Difference shows cache benefit: ~170x faster
```

### Technique 3: Log Analysis

```bash
# View all cache hits
docker compose logs rick-morty-api | grep '"cache_status":"hit"'

# View all cache misses
docker compose logs rick-morty-api | grep '"cache_status":"miss"'

# Count hits vs misses
docker compose logs rick-morty-api | \
  jq -s 'group_by(.cache_status) | map({(.[0].cache_status): length})'
```

### Technique 4: JSON Response Inspection

```bash
curl -s http://localhost:5000/characters?page=1 | jq '._cache'

# Output:
# {
#   "status": "hit",
#   "key": "cache:characters:get:page=1_limit=10",
#   "age_seconds": 45,
#   "ttl_seconds": 255,
#   "stored_at": "2026-09-13T02:20:15Z"
# }
```

### Technique 5: Monitoring Script

```python
#!/usr/bin/env python
"""Monitor cache hit ratio"""

import requests
import time
from collections import defaultdict

def monitor_cache(endpoint: str, duration_seconds: int = 60):
    """Monitor cache hit ratio over time"""
    
    cache_stats = defaultdict(int)
    request_times = {"hit": [], "miss": []}
    
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        # Make request
        start = time.time()
        response = requests.get(endpoint)
        elapsed = time.time() - start
        
        # Extract cache status
        cache_status = response.headers.get("X-Cache", "unknown")
        cache_stats[cache_status] += 1
        request_times[cache_status].append(elapsed * 1000)
        
        # Print stats every 10 requests
        total = sum(cache_stats.values())
        if total % 10 == 0:
            hit_ratio = cache_stats["hit"] / total * 100
            print(f"Total: {total} | Hits: {cache_stats['hit']} | "
                  f"Misses: {cache_stats['miss']} | Hit Ratio: {hit_ratio:.1f}%")
        
        time.sleep(0.5)
    
    # Final stats
    print("\n=== Final Cache Statistics ===")
    print(f"Total Requests: {sum(cache_stats.values())}")
    print(f"Cache Hits: {cache_stats['hit']}")
    print(f"Cache Misses: {cache_stats['miss']}")
    hit_ratio = cache_stats['hit'] / sum(cache_stats.values()) * 100
    print(f"Hit Ratio: {hit_ratio:.1f}%")
    
    if request_times['hit']:
        avg_hit = sum(request_times['hit']) / len(request_times['hit'])
        print(f"Avg Hit Response: {avg_hit:.2f}ms")
    
    if request_times['miss']:
        avg_miss = sum(request_times['miss']) / len(request_times['miss'])
        print(f"Avg Miss Response: {avg_miss:.2f}ms")

if __name__ == "__main__":
    monitor_cache("http://localhost:5000/characters?page=1", duration_seconds=60)
```

---

## Advanced Topics

### Topic 1: Conditional Caching

Serve cached response only if conditions met:

```python
def should_use_cache(request):
    """Determine if request should use cache"""
    
    # Never cache for certain users
    user_id = request.headers.get("X-User-ID")
    if user_id in ADMIN_USERS:
        return False
    
    # Never cache unsafe methods
    if request.method != "GET":
        return False
    
    # Never cache if specific headers present
    if request.headers.get("Cache-Control") == "no-cache":
        return False
    
    # Never cache if requested with bypass
    if request.args.get("cache") == "bypass":
        return False
    
    return True
```

### Topic 2: Cache Invalidation Strategies

When to bust cache:

```python
def invalidate_cache_for_update(entity_type: str, entity_id: int):
    """Invalidate cache when data changes"""
    
    backend = get_cache_backend()
    
    # Strategy 1: Invalidate specific key
    cache_key = f"cache:{entity_type}:get:{entity_id}"
    backend.delete(cache_key)
    
    # Strategy 2: Invalidate related keys
    related_keys = backend.find_keys(f"cache:{entity_type}:*")
    for key in related_keys:
        backend.delete(key)
    
    # Strategy 3: Tag-based invalidation
    if hasattr(backend, 'invalidate_tag'):
        backend.invalidate_tag(f"entity:{entity_type}:{entity_id}")
    
    logger.info(
        "Cache invalidated",
        entity_type=entity_type,
        entity_id=entity_id
    )
```

### Topic 3: Cache Warming

Pre-populate cache with hot data:

```python
def warm_cache():
    """Warm cache with popular data"""
    
    backend = get_cache_backend()
    client = RickAndMortyClient()
    
    # Warm top pages
    for page in [1, 2, 3]:
        for limit in [10, 25, 50]:
            cache_key = f"cache:characters:get:page={page}_limit={limit}"
            
            data = client.fetch_characters(page=page)
            backend.set(cache_key, data, ttl_seconds=3600)
            
            logger.info(f"Warmed cache for page {page}")


@app.before_first_request
def startup_cache_warming():
    """Run cache warming on startup"""
    try:
        warm_cache()
    except Exception as e:
        logger.warning(f"Cache warming failed: {e}")
```

### Topic 4: Cache Analytics Dashboard

Visualize cache performance:

```python
@app.route("/api/cache/analytics", methods=["GET"])
def get_cache_analytics():
    """Get cache analytics for dashboard"""
    
    backend = get_cache_backend()
    stats = backend.get_stats()
    
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cache_backend": stats["backend"],
        "total_requests": stats["hits"] + stats["misses"],
        "hit_ratio_percent": stats["hit_ratio"],
        "hits": stats["hits"],
        "misses": stats["misses"],
        "errors": stats["errors"],
        "performance": {
            "avg_cache_ms": 2.5,
            "avg_origin_ms": 850,
            "avg_savings_ms": 847.5,
            "total_time_saved_seconds": 12710  # (avg_savings * total_requests) / 1000
        }
    }), 200
```

---

## Troubleshooting

### Issue 1: X-Cache Header Not Appearing

**Problem**: Response doesn't have X-Cache header

**Diagnosis**:
```bash
curl -v http://localhost:5000/characters
# Look for: < X-Cache:
```

**Solutions**:
1. Check `add_cache_response_headers()` is registered as `@app.after_request`
2. Verify cache detection middleware runs
3. Check for exceptions in Flask logs
4. Ensure response is not an error (header may not be set on 500s)

### Issue 2: Cache Always Shows MISS

**Problem**: Even repeated requests show cache status as "miss"

**Diagnosis**:
```python
# Check cache backend is working
from config import get_cache_backend
backend = get_cache_backend()
backend.ping()  # Should return True
backend.set("test_key", {"test": "data"}, ttl_seconds=60)
backend.get("test_key")  # Should return the data
```

**Solutions**:
1. Verify Redis is running: `docker compose ps redis`
2. Check cache backend initialization in config.py
3. Look for exceptions in "Cache detection failed" logs
4. Verify cache keys are being generated consistently
5. Check TTL isn't expiring immediately

### Issue 3: Cache Keys Have Collision

**Problem**: Different requests returning same cached data

**Solutions**:
1. Include more request parameters in key generation
2. Add user ID or session to cache key
3. Add timestamp or version to key
4. Use endpoint-specific key generation

### Issue 4: Redis Connection Fails

**Problem**: Cache operations fail with connection error

**Solutions**:
```python
# Check Redis connectivity
import redis
try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    r.ping()
    print("Redis connected")
except Exception as e:
    print(f"Redis error: {e}")

# Check Redis in Docker
docker compose exec redis redis-cli ping
# Should output: PONG

# Check network connectivity
docker compose logs redis
docker compose logs rick-morty-api
```

### Issue 5: Stale Cache Being Served

**Problem**: Cache returning old data even though it should be fresh

**Solutions**:
```python
# Check TTL on keys
import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)
ttl = r.ttl("cache:characters:get:page=1_limit=10")
print(f"TTL remaining: {ttl} seconds")

# Manual cache invalidation
backend.delete("cache:characters:get:page=1_limit=10")

# Check cache warming isn't locking old data
warm_cache()  # Re-run to update

# Monitor cache age in logs
docker compose logs rick-morty-api | jq '.cache_age_seconds'
```

---

## Summary Table

| Method | Visibility | Overhead | Accuracy | Best For |
|--------|-----------|----------|----------|----------|
| Response Headers | Client-side | None | 100% | General use |
| Response Body | Client-side | +50-100 bytes | 100% | Rich info |
| Logs | Backend-only | Low | 100% | Monitoring |
| Query Parameter | Debugging | None | 100% | Testing |
| Performance Metrics | Analytics | Low | 90%+ | Optimization |

---

**Status**: Ready for Implementation  
**Complexity**: Medium (3-4 hours to implement all features)  
**Dependencies**: Redis (already available), Flask (already used)  
**Testing Required**: Response headers, cache detection, log output

