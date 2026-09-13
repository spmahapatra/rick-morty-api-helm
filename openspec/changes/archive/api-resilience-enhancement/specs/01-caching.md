# Caching Layer Specification

## Feature: Redis Caching for Query Results

### Functional Requirements

#### REQ-1.1: Cache Decorator & Abstraction
- Implement a `@cached` decorator for Flask routes
- Support configurable TTL per route (default: 300s for `/characters`, 3600s for individual lookups)
- Cache key generation: `{namespace}:{endpoint}:{query_params_hash}`
- Clear cache on invalid parameters (negative page numbers, invalid sort fields)

**Acceptance Criteria:**
- Cache decorator can be applied to multiple routes without code duplication
- TTL configuration is externalized to environment variables
- Cache keys are deterministic and unique per query signature

#### REQ-1.2: Multi-Backend Support
- Primary backend: Redis (connection pooling, retry on connection loss)
- Fallback backend: In-memory cache for development (no external dependency)
- Automatic backend selection based on environment
- Connection validation on startup (fail fast if Redis unavailable in prod)

**Acceptance Criteria:**
- Application starts successfully in dev without Redis
- Production mode refuses to start without Redis connectivity
- Cache misses transparently fall through to source API

#### REQ-1.3: Cache Invalidation Strategy
- TTL-based expiration (passive invalidation on read)
- Manual invalidation endpoint: `DELETE /cache/{key}` (admin only)
- Cascade invalidation: Invalidate `/characters` cache when character detail is updated
- Warm-up strategy: Pre-populate cache on startup with common queries

**Acceptance Criteria:**
- Expired cache entries do not serve stale data
- Cache can be selectively cleared for testing
- Common queries benefit from startup warming

#### REQ-1.4: Cache Statistics & Observability
- Track cache hits, misses, evictions per endpoint
- Expose cache stats via `/metrics` endpoint
- Log cache operations (GET, SET, INVALIDATE) at DEBUG level
- Include cache status in health check output

**Acceptance Criteria:**
- Metrics show hit ratio calculation: hits / (hits + misses)
- Cache status is available to external monitoring systems
- Health check includes "cache_status": "healthy|degraded|unavailable"

### Performance Requirements

- Cache retrieval: < 5ms (p99)
- Cache write: < 10ms (p99)
- Cache miss rate: < 20% for normal workload patterns
- Memory efficiency: Maximum 100MB cache size (eviction policy: LRU)

### Configuration Requirements

```env
CACHE_BACKEND=redis              # Options: redis, memory
CACHE_TTL_SECONDS=300            # Default TTL
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_POOL_SIZE=10
CACHE_REDIS_SOCKET_TIMEOUT=5
CACHE_WARMUP_ENABLED=true
```

---

## Feature: Result Caching Scenarios

### Scenario 1: Happy Path - Cache Hit
**Given** a client requests `/characters?page=1&limit=10`
**And** this query was executed in the last 300 seconds
**When** a new request arrives with identical parameters
**Then** the response is served from cache
**And** latency is < 10ms
**And** cache hit is logged

### Scenario 2: Cache Expiration & Refresh
**Given** a cached result has TTL of 300 seconds
**And** 300+ seconds have elapsed
**When** a client requests the same query
**Then** the cache is bypassed
**And** a fresh query hits the upstream API
**And** the new result is cached
**And** the operation is logged as "cache_miss" with "reason": "ttl_expired"

### Scenario 3: Invalid Parameters Bypass Cache
**Given** a client requests `/characters?page=-1&limit=0`
**And** these parameters fail validation
**When** parameter validation occurs
**Then** no cache lookup is performed
**And** the request proceeds to validation error handling
**And** "cache_action": "bypassed" is logged

### Scenario 4: Graceful Fallback to No Cache
**Given** Redis is unreachable or slow
**When** a cache operation times out after 5 seconds
**Then** the system logs a warning
**And** proceeds directly to source API (no cache blocking)
**And** the response is still cached for future requests if Redis recovers
**And** health check reports "cache_status": "degraded"

### Scenario 5: Selective Cache Invalidation
**Given** an admin calls `DELETE /cache/characters:*`
**When** the invalidation endpoint is hit
**Then** all character-related cache entries are deleted
**And** subsequent requests fetch fresh data
**And** an audit log records: "action": "cache_invalidation", "keys_pattern": "characters:*"

---

## Feature: Cache-Aware Error Handling

### Scenario 6: Upstream API Failure with Cached Fallback
**Given** the Rick and Morty API is returning 503 Service Unavailable
**And** cached data exists (even if expired)
**When** a request arrives for that cached query
**Then** return the cached result with stale data indicator
**And** include headers: `X-Cache-Status: stale`, `Cache-Control: max-age=0`
**And** log warning: "serving stale cache due to upstream failure"

### Scenario 7: Cache Stampede Prevention
**Given** 100 concurrent requests arrive for an expired cache key
**When** the first request resets the cache
**Then** remaining 99 requests do NOT simultaneously hammer upstream API
**And** a "cache_refresh_lock" mechanism ensures single upstream request
**And** once refreshed, all 99 requests receive the updated cache
**And** log shows: "cache_stampede_prevented", "locked_requests": 98

---

## Non-Functional Requirements

| Requirement | Target | Priority |
|---|---|---|
| Cache availability in production | 99.99% | P0 |
| Graceful degradation if cache unavailable | Required | P0 |
| Cache lookup latency | < 5ms p99 | P1 |
| Memory footprint | < 100MB | P1 |
| Cache key namespace isolation | Complete | P1 |
| Support for cache versioning | v1, v2, etc. | P2 |

---

## API Contract

### New Endpoints

#### GET /metrics
Returns cache and application metrics.
```json
{
  "cache": {
    "hits": 4521,
    "misses": 892,
    "hit_ratio": 0.835,
    "evictions": 12,
    "memory_bytes": 45000000,
    "backend": "redis",
    "status": "healthy"
  },
  "request": {
    "total": 5413,
    "errors": 34,
    "error_rate": 0.0063,
    "avg_latency_ms": 145,
    "p99_latency_ms": 1240
  }
}
```

#### DELETE /cache/{key_pattern}
Invalidate cache entries matching pattern (admin only).
```
DELETE /cache/characters:*
X-Admin-Token: <token>

Response: 200 OK
{
  "invalidated": 23,
  "pattern": "characters:*"
}
```

---

## Testing Requirements

- Unit tests for cache decorator (hit/miss/expiration scenarios)
- Integration tests with real Redis instance
- Load tests: Verify cache prevents thundering herd with 1000+ concurrent requests
- Failure scenario tests: Redis unavailable, timeout, connection loss
- Cache invalidation verification: Ensure stale data never serves beyond TTL + 5s buffer

---

## Documentation

- Configuration guide: Environment variables and backend selection
- Troubleshooting: Common cache issues and diagnostics
- Performance tuning: TTL selection, eviction policy, memory management
- Monitoring: Metrics interpretation and alerting thresholds
