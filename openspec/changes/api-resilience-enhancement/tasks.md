# API Resilience Enhancement - Implementation Tasks

## Overview
31 implementation tasks organized by feature layer. Each task has acceptance criteria and verification steps. Estimated total: 40-50 hours.

---

## Phase 1: Foundation & Infrastructure (Days 1-2)

### Task 1.1: Project Structure & Configuration Management
**Description:** Set up project directories, configuration management, and environment handling.

**Acceptance Criteria:**
- ✅ New directory structure: `app/`, `tests/`, `config/`, `migrations/`, `charts/`
- ✅ `config.py` supports loading from environment variables with defaults
- ✅ `.env.example` documents all configuration parameters
- ✅ Application can run with minimal config in development
- ✅ All sensitive data loads from environment, not committed to git

**Verification:**
```bash
# Configuration should load without errors
FLASK_ENV=development python app/main.py --check-config
# Should output all active configuration values
```

**Effort:** 2 hours

---

### Task 1.2: Logging Infrastructure Setup
**Description:** Implement structured JSON logging with correlation IDs.

**Acceptance Criteria:**
- ✅ `StructuredLogger` class formats all logs as JSON Lines
- ✅ Every request gets a unique correlation ID (generated or from header)
- ✅ Correlation ID present in all logs for that request
- ✅ Log output to stdout (for container/K8s collection)
- ✅ Logs include: timestamp, level, correlation_id, service, version, message, context
- ✅ Configurable log level via environment variable
- ✅ Non-sensitive data only (no passwords, tokens, PII)

**Verification:**
```bash
# Start application with LOG_LEVEL=INFO
python app/main.py 2>&1 | head -1 | python -m json.tool
# Should output valid JSON with all required fields

# Correlation ID should appear in every log
python app/main.py 2>&1 | grep -c '"correlation_id"' | should be > 0
```

**Effort:** 3 hours

---

### Task 1.3: Application Framework & Basic Routes
**Description:** Convert existing Flask app into modular structure with middleware.

**Acceptance Criteria:**
- ✅ Flask app structured with blueprints (routes, handlers)
- ✅ Middleware stack: correlation ID, request logging, CORS, error handling
- ✅ All existing endpoints work: /, /health, /characters, /characters/<id>
- ✅ Request/response logging middleware in place
- ✅ Global error handler returns consistent error response format
- ✅ Tests pass for all existing functionality

**Verification:**
```bash
# Test existing endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/characters?page=1
curl http://localhost:5000/characters/1
# All should return 200 with JSON response
```

**Effort:** 4 hours

---

## Phase 2: Caching Layer (Days 3-5)

### Task 2.1: Cache Backend Abstraction
**Description:** Implement cache interface and both Redis and in-memory backends.

**Acceptance Criteria:**
- ✅ Abstract `CacheBackend` interface with: get(), set(), delete(), exists(), clear()
- ✅ `RedisBackend` implementation with connection pooling (pool_size configurable)
- ✅ `InMemoryBackend` implementation with TTL-based expiration
- ✅ Configuration selects backend: `CACHE_BACKEND=redis` or `memory`
- ✅ Connection pooling: min 5, max 20 connections for Redis
- ✅ Socket timeout: 5 seconds (configurable via environment)
- ✅ All backends handle timeout gracefully (no exceptions bubble up)

**Verification:**
```bash
# Test Redis backend
CACHE_BACKEND=redis python -c "
from app.cache import get_cache_backend
cache = get_cache_backend()
cache.set('test_key', {'data': 'value'}, ttl_seconds=300)
assert cache.get('test_key') == {'data': 'value'}
print('Redis backend: PASS')
"

# Test in-memory backend
CACHE_BACKEND=memory python -c "
from app.cache import get_cache_backend
cache = get_cache_backend()
cache.set('test_key', {'data': 'value'}, ttl_seconds=1)
assert cache.get('test_key') == {'data': 'value'}
import time; time.sleep(1.1)
assert cache.get('test_key') is None
print('In-memory backend: PASS')
"
```

**Effort:** 4 hours

---

### Task 2.2: Cache Decorator & Route Caching
**Description:** Implement `@cached` decorator for automatic query result caching.

**Acceptance Criteria:**
- ✅ `@cached(ttl=300)` decorator applied to `/characters` and `/characters/<id>` routes
- ✅ Cache key generated deterministically: `{endpoint}:{query_params_hash}`
- ✅ Cache miss calls underlying function, stores result, returns
- ✅ Cache hit skips function, returns cached result
- ✅ Expires on TTL (collections: 300s, individual items: 3600s)
- ✅ Invalid parameters bypass cache (negative page, invalid sort)
- ✅ Cache decorator logs: `cache_action`, `cache_hit`, `cache_ttl_remaining`

**Verification:**
```bash
# Test cache hit
curl http://localhost:5000/characters?page=1 -H "X-Correlation-ID: test1"
# Check logs: cache_action="cache_miss"

curl http://localhost:5000/characters?page=1 -H "X-Correlation-ID: test2"
# Check logs: cache_action="cache_hit", response_time_ms should be << first request

# Test invalid parameters bypass cache
curl http://localhost:5000/characters?page=-1
# Should not be cached, return validation error
```

**Effort:** 3 hours

---

### Task 2.3: Cache Statistics & Metrics Endpoint
**Description:** Track cache operations and expose via `/metrics` endpoint.

**Acceptance Criteria:**
- ✅ Track per-endpoint: hits, misses, evictions
- ✅ Calculate: hit_ratio = hits / (hits + misses)
- ✅ Track cache backend status: connected, latency, memory usage
- ✅ `/metrics` endpoint returns JSON with cache stats
- ✅ Stats update in real-time
- ✅ Health check includes `cache_status` field

**Verification:**
```bash
# Make several requests to /characters
for i in {1..5}; do curl http://localhost:5000/characters?page=1; done

# Check metrics
curl http://localhost:5000/metrics | jq '.cache'
# Should show: hits: 4, misses: 1, hit_ratio: 0.8
```

**Effort:** 2 hours

---

### Task 2.4: Cache Invalidation Strategy
**Description:** Implement TTL-based and manual cache invalidation.

**Acceptance Criteria:**
- ✅ Entries expire after TTL (passive invalidation on read)
- ✅ Manual invalidation: `DELETE /cache/{pattern}` endpoint (admin only)
- ✅ Clear related caches on update: e.g., invalidate `/characters` when character detail updated
- ✅ Startup: Option to pre-warm cache with common queries
- ✅ Invalidation logged: `action: cache_invalidation, keys_invalidated: 5`

**Verification:**
```bash
# Test TTL expiration
CACHE_BACKEND=memory python -c "
from app.cache import get_cache_backend
cache = get_cache_backend()
cache.set('key', 'value', ttl_seconds=1)
import time
assert cache.get('key') == 'value'
time.sleep(1.1)
assert cache.get('key') is None
print('TTL expiration: PASS')
"

# Test manual invalidation
curl -X DELETE http://localhost:5000/cache/characters:* -H "X-Admin-Token: secret"
# Should return 200 with invalidated count
```

**Effort:** 2 hours

---

### Task 2.5: Caching Integration Tests
**Description:** Comprehensive tests for caching layer.

**Acceptance Criteria:**
- ✅ Unit tests: Decorator, backend implementations, TTL
- ✅ Integration tests: Redis real instance, concurrent access
- ✅ Load tests: 1000 concurrent requests, 80%+ hit ratio
- ✅ Failure tests: Redis unavailable, timeout, stale cache
- ✅ All tests pass with 90%+ coverage for cache module

**Verification:**
```bash
pytest tests/cache/ -v --cov=app.cache --cov-report=term-missing
# Should show: PASSED, coverage > 90%
```

**Effort:** 3 hours

---

## Phase 3: Persistence Layer (Days 6-9)

### Task 3.1: Database Schema & Migrations
**Description:** Design and implement PostgreSQL schema with Alembic migrations.

**Acceptance Criteria:**
- ✅ `characters` table: id (PK), name, status, species, type, gender, origin*, location*, image_url, created_at, updated_at, synced_at
- ✅ `query_results` table: id (PK), query_params (JSONB), result_count, result_data (JSONB), created_at, expires_at
- ✅ `api_calls` table: id (PK), endpoint, request_params (JSONB), response_status_code, response_time_ms, cache_hit, retry_count, error_message, correlation_id, created_at
- ✅ `metrics` table: id (PK), endpoint, timestamp, request_count, error_count, cache_hits, cache_misses, latency_p50/p95/p99
- ✅ Indexes on: characters(status,species,origin_name), api_calls(correlation_id, created_at), metrics(endpoint, timestamp)
- ✅ Alembic migration files created and tested
- ✅ Auto-migrate on app startup if `DATABASE_AUTO_MIGRATE=true`

**Verification:**
```bash
# Run migrations
alembic upgrade head
# Should output: INFO  [alembic.runtime.migration] Running upgrade 

# Verify schema
psql rickmorty -c "\dt"
# Should show: characters, query_results, api_calls, metrics tables

psql rickmorty -c "\di"
# Should show: created indexes
```

**Effort:** 5 hours

---

### Task 3.2: Connection Pool & Database Layer
**Description:** Implement SQLAlchemy with connection pooling and exception handling.

**Acceptance Criteria:**
- ✅ SQLAlchemy engine configured with pool: `QueuePool(pool_size=5, max_overflow=15, pool_recycle=3600)`
- ✅ Connection timeout: 30 seconds
- ✅ Query timeout: 30 seconds via `connect_args`
- ✅ Pool status tracked: active, idle, queued connections
- ✅ Stale connection detection and recycling
- ✅ Connection exhaustion → return 503 with `Retry-After` header
- ✅ Health check includes pool utilization

**Verification:**
```bash
# Monitor pool during load test
ab -n 100 -c 50 http://localhost:5000/characters

# Check health check output
curl http://localhost:5000/healthcheck | jq '.dependencies.database.details.active_connections'
# Should be <= 20
```

**Effort:** 3 hours

---

### Task 3.3: Repository Pattern & Data Access
**Description:** Implement repository classes for each data model.

**Acceptance Criteria:**
- ✅ `CharacterRepository`: create(), update(), find_by_id(), find_by_filters()
- ✅ `QueryResultRepository`: store_result(), find_result(), cleanup_expired()
- ✅ `ApiCallRepository`: log_call(), find_by_correlation_id(), cleanup_old_records()
- ✅ `MetricsRepository`: record_metrics(), get_metrics_by_endpoint()
- ✅ All repositories use parameterized queries (SQL injection prevention)
- ✅ Upsert logic with ON CONFLICT DO UPDATE for character inserts
- ✅ Transaction handling for multi-table operations

**Verification:**
```bash
# Test character upsert
python -c "
from app.repository import CharacterRepository
repo = CharacterRepository()
char = {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'}
repo.upsert(char)
repo.upsert(char)  # Second insert should update
result = repo.find_by_id(1)
assert result['name'] == 'Rick Sanchez'
print('Upsert: PASS')
"
```

**Effort:** 4 hours

---

### Task 3.4: Data Synchronization Strategy
**Description:** Implement sync logic to persist upstream API data.

**Acceptance Criteria:**
- ✅ On cache miss: Fetch upstream API → store in database → cache result
- ✅ Incremental sync: Only fetch records modified since last sync (via `synced_at`)
- ✅ Batch sync: Process 50 characters at a time
- ✅ `/data-sync` endpoint triggers manual sync
- ✅ Background job (or scheduled task) runs incremental sync hourly
- ✅ Sync errors logged but don't block response to user
- ✅ Sync operation logged: duration, records processed, errors

**Verification:**
```bash
# Test sync on cache miss
curl http://localhost:5000/characters/1

# Verify in database
psql rickmorty -c "SELECT id, name FROM characters WHERE id=1"
# Should show character record

# Test manual sync
curl -X POST http://localhost:5000/data-sync -H "X-Admin-Token: secret"
# Should return 202 Accepted with sync status
```

**Effort:** 3 hours

---

### Task 3.5: Persistence Integration Tests
**Description:** Test database layer functionality.

**Acceptance Criteria:**
- ✅ Unit tests: Repository CRUD operations, upsert logic, queries
- ✅ Integration tests: Real PostgreSQL, transactions, indexes
- ✅ Failure tests: Connection loss, query timeout, pool exhaustion
- ✅ Data integrity tests: No duplicates, race conditions handled
- ✅ Performance tests: Query latency, index efficiency
- ✅ All tests pass with 85%+ coverage for repository module

**Verification:**
```bash
pytest tests/persistence/ -v --cov=app.repository --cov-report=term-missing
# Should show: PASSED, coverage > 85%
```

**Effort:** 3 hours

---

## Phase 4: Resilience Patterns (Days 10-12)

### Task 4.1: Exponential Backoff Retry Logic
**Description:** Implement retry mechanism with exponential backoff and jitter.

**Acceptance Criteria:**
- ✅ `RetryPolicy` class with: max_attempts=5, base_delay=100ms, max_delay=30s
- ✅ Backoff formula: `delay = min(base * (2^n), max_delay) * (1 ± jitter)`
- ✅ Retry on: 429, 503, connection timeout, socket errors
- ✅ Non-retryable: 400, 404, 401, 403 (fail fast)
- ✅ Jitter prevents thundering herd: ±20% random variation
- ✅ Logging shows: `retry_attempt: 2/5, next_retry_ms: 212, error: ConnectionTimeout`
- ✅ Configuration: `RETRY_ENABLED`, `RETRY_MAX_ATTEMPTS`, `RETRY_BASE_DELAY_MS`, `RETRY_MAX_DELAY_MS`

**Verification:**
```bash
# Test retry logic
python -c "
from app.resilience import RetryPolicy
from unittest.mock import Mock
import time

policy = RetryPolicy(max_attempts=3, base_delay=10)
calls = []

def failing_func():
    calls.append(time.time())
    if len(calls) < 3:
        raise ConnectionError('Network error')
    return 'success'

result = policy.execute(failing_func)
assert result == 'success'
assert len(calls) == 3
print(f'Retry: PASS ({len(calls)} attempts)')
"
```

**Effort:** 4 hours

---

### Task 4.2: Circuit Breaker Pattern Implementation
**Description:** Implement circuit breaker with state machine (CLOSED → OPEN → HALF_OPEN).

**Acceptance Criteria:**
- ✅ State machine: CLOSED (normal) → OPEN (fail fast) → HALF_OPEN (probe)
- ✅ CLOSED: Track failures, threshold=5, success_threshold=10 resets counter
- ✅ OPEN: Reject immediately for 60 seconds, return 503 with `Retry-After: 60`
- ✅ HALF_OPEN: Allow limited probes (max 3), 2+ success → CLOSED, 1+ fail → OPEN
- ✅ State transitions logged: `circuit_breaker_state_change: CLOSED -> OPEN`
- ✅ Configuration: `CIRCUIT_BREAKER_FAILURE_THRESHOLD`, `CIRCUIT_BREAKER_RESET_TIMEOUT_S`

**Verification:**
```bash
# Test circuit breaker state transitions
python -c "
from app.resilience import CircuitBreaker

cb = CircuitBreaker(failure_threshold=3, reset_timeout_s=1)

# CLOSED -> OPEN after 3 failures
for i in range(3):
    try:
        cb.call(lambda: 1/0)  # Raises exception
    except:
        pass

assert cb.state == 'OPEN'
print('Circuit breaker OPEN: PASS')

# Try to call while OPEN
try:
    cb.call(lambda: 'success')
except Exception as e:
    assert 'Circuit breaker' in str(e)
    print('Circuit breaker OPEN rejection: PASS')
"
```

**Effort:** 4 hours

---

### Task 4.3: Timeout Management
**Description:** Implement timeouts across all network operations.

**Acceptance Criteria:**
- ✅ Socket timeout (TCP): 5 seconds
- ✅ Read timeout (HTTP): 10 seconds
- ✅ Total request timeout: 20 seconds
- ✅ Database query timeout: 30 seconds
- ✅ Cache lookup timeout: 2 seconds
- ✅ Health check timeout: 15 seconds
- ✅ All timeouts configurable via environment
- ✅ Timeout exceeded → appropriate error status (504 Gateway Timeout or 503)
- ✅ Logging includes: `timeout_type: read_timeout, timeout_ms: 10000, elapsed_ms: 10023`

**Verification:**
```bash
# Test timeout handling
# Simulate slow upstream API
python -c "
from app.resilience import timeout
import time

@timeout(seconds=2)
def slow_operation():
    time.sleep(3)
    return 'done'

try:
    slow_operation()
except TimeoutError:
    print('Timeout: PASS')
"
```

**Effort:** 2 hours

---

### Task 4.4: Graceful Degradation
**Description:** Implement fallback strategies for dependency failures.

**Acceptance Criteria:**
- ✅ Upstream API down → Try cache (even if expired) + database
- ✅ Cache unavailable → Use database + upstream API
- ✅ Database unavailable → Use cache if available
- ✅ All unavailable → Return 503 with best-effort stale data if exists
- ✅ Response includes: `X-Cache-Status: stale`, `X-Data-Freshness: 5_hours_old`
- ✅ Fallback order: Fresh cache → Database → Stale cache → Error
- ✅ Fallback operations logged with reason: `fallback_source: database, reason: upstream_timeout`

**Verification:**
```bash
# Test fallback to database when cache unavailable
# Simulate Redis down, make request, verify response from database
# Check response headers include X-Cache-Status header
```

**Effort:** 3 hours

---

### Task 4.5: Resilience Integration Tests
**Description:** Test retry, circuit breaker, and fallback behavior.

**Acceptance Criteria:**
- ✅ Unit tests: Retry backoff, circuit breaker states, timeouts
- ✅ Integration tests: Failure injection (503, 429, timeout)
- ✅ Chaos tests: Random failures, cascading failures
- ✅ Recovery tests: Successful recovery after failures
- ✅ All tests pass with 90%+ coverage for resilience module

**Verification:**
```bash
pytest tests/resilience/ -v --cov=app.resilience --cov-report=term-missing
# Should show: PASSED, coverage > 90%
```

**Effort:** 3 hours

---

## Phase 5: Rate Limiting (Days 13-14)

### Task 5.1: Rate Limiting Implementation
**Description:** Implement token bucket rate limiter with per-consumer tiers.

**Acceptance Criteria:**
- ✅ Token bucket algorithm: Refill at constant rate
- ✅ Consumer tiers: Public (100), Standard (1000), Premium (5000) req/min
- ✅ Default (no API key): Public tier
- ✅ Storage: Redis counters (atomic increment)
- ✅ Precision: 1-minute windows (reset on minute boundary)
- ✅ Rate limit middleware checks before route execution
- ✅ Exceeded limit → 429 Too Many Requests
- ✅ Configuration: `RATE_LIMIT_ENABLED`, limits per tier

**Verification:**
```bash
# Test rate limiting
for i in {1..101}; do
    curl http://localhost:5000/characters -s -w "%{http_code}\n" -o /dev/null
done | tail -1
# Last request should be 429

# Check rate limit headers
curl http://localhost:5000/characters -i | grep RateLimit
# Should show: RateLimit-Limit: 100, RateLimit-Remaining: X, RateLimit-Reset: timestamp
```

**Effort:** 3 hours

---

### Task 5.2: API Key Management & Consumer Tiers
**Description:** Implement API key storage and tier-based limiting.

**Acceptance Criteria:**
- ✅ API key format: `sk_` prefix (e.g., `sk_premium_abc123def456`)
- ✅ Keys stored in database with: key_hash, consumer_name, tier, created_at, last_used_at
- ✅ Key hashing: bcrypt for security
- ✅ API key passed via header: `X-API-Key: sk_...`
- ✅ Valid key → Apply tier limit
- ✅ Invalid/revoked key → 401 Unauthorized
- ✅ Admin endpoint to create/revoke keys: `/admin/api-keys`

**Verification:**
```bash
# Create API key
curl -X POST http://localhost:5000/admin/api-keys \
  -H "X-Admin-Token: secret" \
  -d '{"consumer": "test_user", "tier": "standard"}'
# Should return: {key: "sk_...", tier: "standard"}

# Use API key
curl http://localhost:5000/characters -H "X-API-Key: sk_..."
# Should allow 1000 req/min for standard tier
```

**Effort:** 2 hours

---

### Task 5.3: Rate Limit Response Headers
**Description:** Add standard rate limit headers to all responses.

**Acceptance Criteria:**
- ✅ Response headers: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`
- ✅ Headers present in all responses (success and limited)
- ✅ Values accurately reflect current quota and reset time
- ✅ `Retry-After` format: seconds until next available request (on 429)
- ✅ Headers used by clients for intelligent backoff

**Verification:**
```bash
curl -i http://localhost:5000/characters | grep -E "RateLimit|Retry-After"
# Should show: RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset
```

**Effort:** 1 hour

---

### Task 5.4: DDoS Detection & Mitigation
**Description:** Detect and mitigate DDoS patterns.

**Acceptance Criteria:**
- ✅ Spike detection: Flag IP with > 10x normal rate
- ✅ Temporary ban: Rate limit violator IP to 10 req/min for 24 hours
- ✅ Alerting: Log security event `potential_ddos: ip=..., requests_per_minute=50000`
- ✅ Whitelist: Support whitelist for internal IPs, health checks
- ✅ Configuration: `RATE_LIMIT_DDOS_DETECTION_ENABLED`, `RATE_LIMIT_DDOS_THRESHOLD_PER_MINUTE`

**Verification:**
```bash
# Simulate DDoS from single IP
for i in {1..10000}; do
    curl http://localhost:5000/characters -s -o /dev/null &
done
# Check logs for DDoS detection alert
# Verify IP is rate-limited to 10 req/min
```

**Effort:** 2 hours

---

### Task 5.5: Rate Limiting Tests
**Description:** Test rate limiting functionality.

**Acceptance Criteria:**
- ✅ Unit tests: Token bucket algorithm, tier enforcement
- ✅ Integration tests: Redis counter accuracy, window resets
- ✅ Load tests: 1000 concurrent requests, rate limit accuracy within ±1%
- ✅ DDoS simulation: Verify detection and mitigation
- ✅ API key tests: Valid, invalid, revoked keys
- ✅ All tests pass with 85%+ coverage for rate limit module

**Verification:**
```bash
pytest tests/rate_limit/ -v --cov=app.rate_limit --cov-report=term-missing
# Should show: PASSED, coverage > 85%
```

**Effort:** 2 hours

---

## Phase 6: Observability (Days 15-17)

### Task 6.1: Deep Health Check Endpoint
**Description:** Implement `/healthcheck` with deep dependency verification.

**Acceptance Criteria:**
- ✅ Endpoint: `GET /healthcheck` → 200 OK (healthy) or 503 (unhealthy)
- ✅ Checks: Database, Cache, Upstream API, Disk Space, Memory, Filebeat
- ✅ Each check includes: status, latency_ms, checked_at, details, last_error
- ✅ Overall status: healthy (all critical passed), degraded (non-critical failed), unhealthy (critical failed)
- ✅ Each check has timeout: Database 5s, Cache 5s, Upstream 10s, Health 15s total
- ✅ Response includes recommendations based on issues

**Verification:**
```bash
curl http://localhost:5000/healthcheck | jq '.'
# Should show: status, dependencies with sub-status, checks_passed, checks_failed

# Test with Redis down
docker stop redis-container
curl http://localhost:5000/healthcheck | jq '.dependencies.cache.status'
# Should show: unhealthy

# With graceful degradation
curl http://localhost:5000/healthcheck | jq '.status'
# Should show: degraded (not unhealthy, since database and API still work)
```

**Effort:** 3 hours

---

### Task 6.2: Kubernetes Health Probes
**Description:** Implement liveness, readiness, and startup probes.

**Acceptance Criteria:**
- ✅ `/health/live`: Process alive check → 200 OK (fast, < 2 seconds)
- ✅ `/health/ready`: Critical dependencies check → 200 OK or 503 Service Unavailable
- ✅ `/health/startup`: Database migration complete check → 200 OK or 503 Service Unavailable
- ✅ Kubernetes pod configuration uses these probes
- ✅ Probe timeouts: liveness 5s, readiness 10s, startup 30s
- ✅ Failure thresholds: liveness 3 failures (30s), readiness 2 failures (10s)

**Verification:**
```bash
# Test liveness probe
curl http://localhost:5000/health/live
# Should return 200 OK instantly

# Test readiness probe
curl http://localhost:5000/health/ready
# Should return 200 OK if database + cache + API ready

# Test startup probe
curl http://localhost:5000/health/startup
# Should return 503 while starting, then 200 OK
```

**Effort:** 2 hours

---

### Task 6.3: Metrics Collection & Exposition
**Description:** Collect and expose application metrics.

**Acceptance Criteria:**
- ✅ Metrics tracked: Requests per endpoint, error rate, latencies (p50/p95/p99), cache hits/misses
- ✅ `/metrics` endpoint returns Prometheus-compatible format
- ✅ Per-endpoint metrics: request_count, error_count, latency distribution
- ✅ Cache metrics: hits, misses, hit_ratio, evictions
- ✅ Database metrics: connection pool utilization, query latencies
- ✅ Upstream API metrics: latency, error rate, circuit breaker state
- ✅ Metrics aggregated per 1-minute bucket

**Verification:**
```bash
curl http://localhost:5000/metrics | head -20
# Should show Prometheus-format metrics:
# api_requests_total{endpoint="/characters", method="GET", status="200"} 150

# Verify metrics accuracy
ab -n 100 -c 10 http://localhost:5000/characters
curl http://localhost:5000/metrics | grep api_requests_total
# request count should increase by ~100
```

**Effort:** 3 hours

---

### Task 6.4: Filebeat Log Shipping Integration
**Description:** Set up Filebeat to ship logs to ELK stack.

**Acceptance Criteria:**
- ✅ Application logs to stdout as JSON Lines
- ✅ Filebeat container configured to read stdout
- ✅ Filebeat parses JSON and indexes into Logstash
- ✅ Logstash enriches logs and forwards to OpenSearch
- ✅ Correlation IDs enable full request tracing in OpenSearch
- ✅ Docker Compose includes Filebeat service
- ✅ Logs visible in OpenSearch Dashboard after 2-5 seconds

**Verification:**
```bash
# Make requests to application
curl http://localhost:5000/characters

# Check Filebeat logs
docker logs filebeat-container | tail -5
# Should show logs being shipped

# Check OpenSearch (if available)
curl http://localhost:9200/logs-*/_search | jq '.hits.hits | length'
# Should show indexed documents
```

**Effort:** 2 hours

---

### Task 6.5: Request Tracing via Correlation IDs
**Description:** Enable request tracing using correlation IDs.

**Acceptance Criteria:**
- ✅ Correlation ID generated if not provided in header
- ✅ ID format: `{service}_{timestamp}_{random}` e.g., `api_20240913_101532_abc123`
- ✅ ID propagated to all downstream calls (cache, database, upstream API)
- ✅ ID stored in database audit trail
- ✅ Query by correlation ID shows full request lifecycle across all logs
- ✅ Filebeat/ELK enables searching by correlation_id

**Verification:**
```bash
# Make request
CORR_ID="trace_$(date +%s)"
curl http://localhost:5000/characters -H "X-Correlation-ID: $CORR_ID" -H "X-Correlation-ID: $CORR_ID"

# Search logs by correlation ID
grep "$CORR_ID" application.log | jq '.event_type'
# Should show: character_fetch, cache_lookup, database_query, etc. all with same correlation_id

# Search in ELK/OpenSearch
# Query: correlation_id: $CORR_ID
# Should show timeline of all operations for that request
```

**Effort:** 2 hours

---

### Task 6.6: Observability Tests
**Description:** Test logging, health checks, and metrics.

**Acceptance Criteria:**
- ✅ Unit tests: Log formatting (valid JSON), health check logic
- ✅ Integration tests: Health check with dependencies, metrics accuracy
- ✅ End-to-end tests: Correlation ID propagation, full request logging
- ✅ All tests pass with 80%+ coverage for observability module

**Verification:**
```bash
pytest tests/observability/ -v --cov=app.observability --cov-report=term-missing
# Should show: PASSED, coverage > 80%
```

**Effort:** 2 hours

---

## Phase 7: DevOps & Deployment (Days 18-20)

### Task 7.1: Docker Compose Local Development
**Description:** Create Docker Compose file for complete stack.

**Acceptance Criteria:**
- ✅ Services: app (Flask), redis, postgres, filebeat
- ✅ Volumes: PostgreSQL data persistence, shared logs
- ✅ Environment: All services auto-configured via docker-compose.yml
- ✅ Networks: All services on same network (app → redis, postgres)
- ✅ Health checks: Compose waits for dependent services
- ✅ Startup: `docker-compose up` brings up fully functional stack
- ✅ Cleanup: `docker-compose down` cleanly shuts down

**Verification:**
```bash
docker-compose up -d
sleep 10
curl http://localhost:5000/health
# Should return 200 OK

docker-compose ps
# All services should show "healthy" or "running"

docker-compose down
```

**Effort:** 3 hours

---

### Task 7.2: Docker Image Optimization
**Description:** Create optimized Dockerfile for production.

**Acceptance Criteria:**
- ✅ Multi-stage build: First stage installs dependencies, second stage runs app
- ✅ Base image: `python:3.11-slim` (small footprint)
- ✅ Non-root user: App runs as non-root for security
- ✅ Health check: Dockerfile includes HEALTHCHECK instruction
- ✅ Image size: < 200MB
- ✅ Caching: Layers ordered to maximize caching (dependencies before app code)
- ✅ Build: `docker build -t rick-morty-api:v1.0.0 .` succeeds

**Verification:**
```bash
docker build -t rick-morty-api:v1.0.0 .
docker images rick-morty-api
# Should show size < 200MB

docker run -it rick-morty-api:v1.0.0 /bin/sh
# Should be able to start container
```

**Effort:** 2 hours

---

### Task 7.3: GitHub Actions CI/CD Pipeline
**Description:** Implement automated testing and deployment workflow.

**Acceptance Criteria:**
- ✅ Trigger: On push to main branch
- ✅ Steps: Lint → Unit tests → Integration tests → Build Docker image → Push to Docker Hub → Deploy to Minikube
- ✅ Test failure → Stop pipeline, notify
- ✅ Artifacts: Docker image tagged with commit SHA and version
- ✅ Deploy: Helm chart updated on successful build
- ✅ Notification: Success/failure posted to team channel (if configured)

**Verification:**
```bash
# Push commit to main
git add . && git commit -m "test" && git push origin main

# Monitor GitHub Actions
# Should see workflow: Lint → Test → Build → Deploy
# All steps should succeed
```

**Effort:** 4 hours

---

### Task 7.4: Helm Charts for Kubernetes
**Description:** Create Helm charts for production deployment.

**Acceptance Criteria:**
- ✅ Charts structure: `charts/rick-morty-api/`, `charts/redis/`, `charts/postgres/`
- ✅ Values: Configurable via `values.yaml` (replicas, image, resources, limits)
- ✅ Deployment: 3 replicas of app, rolling updates
- ✅ Service: LoadBalancer type on port 5000
- ✅ ConfigMap: Application configuration
- ✅ Secrets: Database credentials (sealed/encrypted)
- ✅ PersistentVolumeClaim: PostgreSQL storage (20GB)
- ✅ Health probes: Liveness, readiness, startup in deployment spec
- ✅ Resource limits: CPU requests/limits, memory requests/limits
- ✅ Helm install: `helm install rick-morty-api charts/rick-morty-api/` deploys to cluster

**Verification:**
```bash
helm install rick-morty-api charts/rick-morty-api/ --values charts/values-dev.yaml
kubectl get deployments
# Should show: rick-morty-api with 3 replicas

kubectl get pods
# Should show: 3 app pods running, database and cache pods ready

curl http://localhost:5000/health
# Should return 200 OK
```

**Effort:** 5 hours

---

### Task 7.5: Kubernetes Deployment & Configuration
**Description:** Deploy to Minikube and verify all features work.

**Acceptance Criteria:**
- ✅ Minikube cluster running: `minikube start`
- ✅ Helm deployment: App, Redis, PostgreSQL all deployed
- ✅ Health probes: Liveness working (pod restart on failure), readiness working (remove from load balancer if unhealthy)
- ✅ Scaling: `kubectl scale` changes replica count dynamically
- ✅ Logs: `kubectl logs` shows JSON structured logs
- ✅ Port forward: `kubectl port-forward` enables local access
- ✅ Monitoring: Prometheus + Grafana stack optional but recommended

**Verification:**
```bash
minikube start
helm install rick-morty-api ./charts/rick-morty-api/

kubectl get pods -w
# Should show: 3 app pods, postgres pod, redis pod all RUNNING

kubectl logs deployment/rick-morty-api | head -1 | python -m json.tool
# Should show valid JSON log

kubectl scale deployment rick-morty-api --replicas=5
kubectl get pods | grep rick-morty-api | wc -l
# Should show 5 pods

# Port forward and test
kubectl port-forward svc/rick-morty-api 5000:5000 &
curl http://localhost:5000/health
```

**Effort:** 4 hours

---

## Phase 8: Integration & Final Testing (Days 21-22)

### Task 8.1: End-to-End Integration Tests
**Description:** Test complete stack with all features.

**Acceptance Criteria:**
- ✅ Happy path: Request → Cache hit → Response (< 50ms)
- ✅ Cache miss: Request → Database/API → Cache → Response
- ✅ Upstream failure: Request → Cache/Database fallback → Response
- ✅ Rate limit: Exceeds limit → 429 with Retry-After
- ✅ Correlation ID: Full tracing through all layers
- ✅ Health checks: All probes return appropriate status
- ✅ Metrics: Counters accurate and exposed
- ✅ Logs: JSON format, searchable by correlation_id

**Verification:**
```bash
pytest tests/integration/ -v --tb=short
# Should show: PASSED for all E2E tests
```

**Effort:** 3 hours

---

### Task 8.2: Performance & Load Testing
**Description:** Validate performance under load.

**Acceptance Criteria:**
- ✅ Cache hit latency: < 50ms (p99)
- ✅ Cache miss latency: < 500ms (p99)
- ✅ Throughput: 1000+ req/sec with 80%+ cache hit ratio
- ✅ Concurrent connections: 500+ simultaneous without degradation
- ✅ Connection pool: < 80% utilization under normal load
- ✅ Memory: < 500MB under sustained 1000 req/sec
- ✅ CPU: < 80% under sustained 1000 req/sec
- ✅ No errors or timeouts during 10-minute load test

**Verification:**
```bash
# Load test with ApacheBench
ab -n 10000 -c 500 http://localhost:5000/characters

# Check latency results
# Should show: Mean latency ~25ms (cache hit)

# Monitor with top/docker stats
docker stats rick-morty-api-container
# Memory and CPU should stay stable
```

**Effort:** 3 hours

---

### Task 8.3: Failure Scenario Testing
**Description:** Test system behavior under various failure modes.

**Acceptance Criteria:**
- ✅ Redis down → App gracefully degrades, uses database
- ✅ PostgreSQL down → App uses cache, returns stale data
- ✅ Upstream API down → Circuit breaker opens, serves cache
- ✅ Network partition → Retries with backoff, circuit breaker
- ✅ All scenarios → Response to user (no 500 errors), appropriate status code (503 if all fail)
- ✅ Recovery → Services restart, app detects recovery, normal operations resume

**Verification:**
```bash
# Stop Redis
docker stop rick-morty-redis
curl http://localhost:5000/characters
# Should return 200 with data from database

# Stop PostgreSQL
docker stop rick-morty-postgres
curl http://localhost:5000/characters
# Should return 200 with stale cache data + warning header

# Kill upstream API (mock failure)
# Circuit breaker should open
# Subsequent requests should fail fast (not retry)
```

**Effort:** 3 hours

---

### Task 8.4: Documentation & Knowledge Transfer
**Description:** Create comprehensive documentation and train team.

**Acceptance Criteria:**
- ✅ Architecture documentation: System diagram, data flow, components
- ✅ API documentation: Endpoints, parameters, examples, error codes
- ✅ Deployment guide: Docker Compose, Kubernetes/Helm, CI/CD
- ✅ Operations guide: Health checks, monitoring, alerting, troubleshooting
- ✅ Configuration reference: All environment variables explained
- ✅ Development guide: Setup, running tests, debugging
- ✅ Team training: Walk-through of key features, demonstrated on working system

**Verification:**
```bash
# Documentation should be in /docs/ directory
ls -la docs/
# Should contain: architecture.md, api.md, deployment.md, operations.md, config.md, development.md

# All docs should be readable and technically accurate
grep -r "TODO\|FIXME" docs/
# Should return no results
```

**Effort:** 4 hours

---

### Task 8.5: Production Readiness Validation
**Description:** Final validation before production launch.

**Acceptance Criteria:**
- ✅ Security: No hardcoded secrets, API keys, or sensitive data in code
- ✅ Performance: All SLIs met (latency, throughput, error rate)
- ✅ Reliability: 99.5% availability demonstrated in staging
- ✅ Monitoring: All critical metrics collected and alertable
- ✅ Logging: All events logged, searchable, correlatable
- ✅ Scalability: Demonstrated scaling to 3 replicas with no issues
- ✅ Disaster recovery: Data loss scenario & recovery procedure documented
- ✅ Rollback plan: Procedure to rollback version if needed
- ✅ Runbooks: Troubleshooting guides for common issues
- ✅ Sign-off: Tech lead and operations sign-off on deployment

**Verification:**
```bash
# Run all tests + checks
pytest tests/ --cov=app --cov-report=term-missing
# Coverage > 85%, all tests pass

# Deploy to staging
helm upgrade rick-morty-api ./charts/rick-morty-api/ --values values-staging.yaml

# Validation
./scripts/production_readiness_check.sh
# Should output: ✅ All checks passed
```

**Effort:** 3 hours

---

## Task Summary

| Phase | Task Count | Estimated Hours | Completion |
|-------|-----------|-----------------|------------|
| 1. Foundation | 3 | 9 | ☐ |
| 2. Caching | 5 | 14 | ☐ |
| 3. Persistence | 5 | 18 | ☐ |
| 4. Resilience | 5 | 16 | ☐ |
| 5. Rate Limiting | 5 | 10 | ☐ |
| 6. Observability | 6 | 14 | ☐ |
| 7. DevOps | 5 | 18 | ☐ |
| 8. Integration | 5 | 16 | ☐ |
| **TOTAL** | **39** | **115** | ☐ |

**Revised Effort Estimate:** 40-50 hours for core implementation (115 hours includes extensive testing and documentation)

---

## Dependencies & Prerequisites

Before starting implementation:
- ✅ Environment: Python 3.9+, Docker, Docker Compose, Kubernetes (Minikube)
- ✅ External services: Docker Hub account for image registry
- ✅ Team: At least 2 developers (one handling backend, one handling DevOps/Kubernetes)
- ✅ Planning: All specification documents reviewed and approved

## Success Metrics

- ✅ All 39 tasks completed
- ✅ Test coverage > 85% for all modules
- ✅ Performance SLIs met: Latency, throughput, availability
- ✅ Zero critical bugs in first 2 weeks post-launch
- ✅ All runbooks documented and validated
- ✅ Team trained and confident in operations
