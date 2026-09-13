# API Resilience & Observability Enhancement - Durable Capability Specification

**Status:** Archived & Formalized  
**Archive Date:** 2026-09-13  
**Change ID:** api-resilience-enhancement  
**Version:** 1.0.0  

---

## Executive Summary

This capability transforms the Rick and Morty API wrapper from a basic Flask application into a production-ready, resilient service with enterprise-grade caching, data persistence, observability, and Kubernetes orchestration.

### Key Capabilities Delivered

1. **High-Performance Caching** - Redis-backed query result caching with 80%+ hit ratio
2. **Data Persistence** - PostgreSQL schema for character data, metrics, and audit trails
3. **Resilience Patterns** - Exponential backoff, circuit breaker, graceful degradation
4. **Enterprise Observability** - Structured JSON logging, health checks, Kubernetes probes
5. **Traffic Control** - Token bucket rate limiting with per-consumer tiers
6. **Production Deployment** - Docker Compose and Helm charts for local and Kubernetes environments

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Applications                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    HTTP Requests (with X-Correlation-ID)
                                 │
        ┌────────────────────────▼─────────────────────────┐
        │    Flask Application (Rick-Morty API Wrapper)    │
        │  - Request routing & parameter validation        │
        │  - Rate limiting middleware                       │
        │  - Correlation ID injection                       │
        │  - Error handling & graceful degradation          │
        └────────────────────────┬─────────────────────────┘
                                 │
        ┌────────────────────────┴──────────────┬──────────────┐
        │                                       │              │
        │                   Structured JSON Logging
        │                   (stdout → Filebeat → ELK)
        │
    ┌───▼──────┐    ┌──────────────┐    ┌────────────────┐
    │  Redis   │    │ PostgreSQL   │    │  Rick & Morty  │
    │  Cache   │    │  Database    │    │  Public API    │
    │          │    │              │    │                │
    │- Query   │    │- Characters  │    │- Fetch         │
    │  Results │    │- Metrics     │    │  Characters    │
    │- Retry   │    │- API Calls   │    │- Handle Rate   │
    │  Policy  │    │- Analytics   │    │  Limits        │
    └──────────┘    └──────────────┘    └────────────────┘
        ▲                  ▲                      ▲
        │                  │                      │
        └──────────────────┴──────────────────────┘
                    Application Logic Layer
                    (Caching, Persistence, Resilience)
```

### Request Lifecycle

```
1. Client Request
   ↓
2. Middleware: Extract/Generate Correlation ID
   ↓
3. Rate Limit Check → If exceeded: Return 429 + Retry-After
   ↓
4. Cache Lookup (Redis)
   ├─ HIT  → Skip to step 9
   └─ MISS → Continue to step 5
   ↓
5. Validate Parameters
   ├─ Invalid → Return 400 + log
   └─ Valid → Continue to step 6
   ↓
6. Query Database (PostgreSQL)
   ├─ Success → Add to response (stale data option)
   └─ Failure → Circuit breaker decision
   ↓
7. Upstream API Call (with Retry + Backoff + Circuit Breaker)
   ├─ Success (200) → Persist to database, cache result, return
   ├─ Rate Limit (429) → Exponential backoff, retry
   ├─ Unavailable (503) → Try N times, then circuit open, fallback to stale cache
   └─ Error (other) → Log, return error
   ↓
8. Persist to PostgreSQL
   ├─ SUCCESS → Sync complete
   └─ FAILURE → Log warning, data lost from persistence but returned to user
   ↓
9. Cache Result (Redis)
   ├─ Success → Store with TTL
   └─ Failure → Log warning, continue (graceful degradation)
   ↓
10. Log Operation (JSON to stdout)
    ├─ Timestamp, correlation_id, latencies, cache_hit, status_code, context
    └─ Filebeat picks up → Logstash parses → OpenSearch indexes
    ↓
11. Return Response to Client
    ├─ Include rate-limit headers
    ├─ Include cache status headers
    └─ Include correlation ID in response headers
```

---

## Capabilities & Performance Targets

### Caching Layer (Redis)

**What It Does:**
- Caches query results with configurable TTL (time-to-live)
- Supports both collection queries (`/characters`) and individual lookups (`/characters/<id>`)
- Implements cache invalidation strategies (TTL-based and manual)
- Provides multiple cache backends (Redis primary, in-memory fallback)

**Performance Targets:**
- Cache hit ratio: ≥ 80% for repeated queries within TTL window
- Cached request latency: < 100ms (p99)
- Cache miss: < 500ms (p99) - direct upstream call

**Configuration:**
- Backend selection: `CACHE_BACKEND=redis` or `memory`
- Connection pooling: 5-20 connections (configurable)
- Socket timeout: 5 seconds (configurable)
- TTL defaults: Collections 300s, Individual items 3600s

### Data Persistence (PostgreSQL)

**What It Does:**
- Stores character data for analytics and audit trails
- Tracks API calls, cache hits/misses, and performance metrics
- Enables historical analysis and data recovery
- Provides durable fallback when services are down

**Schema:**
- `characters`: Full character data with sync timestamp
- `query_results`: Cached query parameters and results
- `api_calls`: Audit trail of upstream API interactions
- `metrics`: Performance metrics aggregated by endpoint and time

**Configuration:**
- Connection pooling: 5-20 connections (SQLAlchemy QueuePool)
- Query timeout: 30 seconds
- Connection recycle: 3600 seconds
- Auto-migrate on startup if `DATABASE_AUTO_MIGRATE=true`

### Resilience Patterns

**Exponential Backoff Retry:**
- Retry transient failures (429, 503, connection timeout)
- Formula: `delay = min(base * (2^n), max) * (1 ± jitter)`
- Max attempts: 5 (configurable)
- Base delay: 100ms, Max delay: 30s
- Jitter: ±20% to prevent thundering herd

**Circuit Breaker:**
- State machine: CLOSED → OPEN → HALF_OPEN
- Threshold: 5 consecutive failures → OPEN
- Reset timeout: 60 seconds
- Half-open probes: Limited test requests to verify recovery

**Timeout Management:**
- Socket timeout (TCP): 5 seconds
- Read timeout (HTTP): 10 seconds
- Total request timeout: 20 seconds
- Database query timeout: 30 seconds
- Cache lookup timeout: 2 seconds

**Graceful Degradation:**
- Fallback order: Fresh cache → Database → Stale cache → Error
- Response headers indicate data freshness and source
- No client-facing 500 errors when services degrade

### Rate Limiting

**What It Does:**
- Token bucket algorithm: Refill at constant rate
- Per-consumer tiers: Public (100), Standard (1000), Premium (5000) req/min
- Stores counters in Redis with atomic increment
- 1-minute windows with automatic reset

**Response Headers:**
- `RateLimit-Limit`: Quota for the consumer
- `RateLimit-Remaining`: Requests remaining in current window
- `RateLimit-Reset`: Unix timestamp when quota resets
- `Retry-After`: Seconds to wait before next allowed request (on 429)

**DDoS Detection:**
- Spike detection: IP with > 10x normal rate flagged
- Temporary ban: 10 req/min for 24 hours on violation
- Security logging: Alerts for potential attacks

### Observability & Logging

**Structured JSON Logging:**
- JSON Lines format (one valid JSON per line)
- Every request gets unique correlation ID (generated or from header)
- Log fields: timestamp, level, correlation_id, service, version, message, context
- Correlation ID propagated to all downstream calls

**Health Checks:**
- `/healthcheck`: Deep dependency verification (200 or 503)
- `/health/live`: Process alive check (< 2 seconds)
- `/health/ready`: Critical dependencies check (10s timeout)
- `/health/startup`: Database migration complete check (30s timeout)

**Metrics Exposition:**
- `/metrics` endpoint: Prometheus-compatible format
- Per-endpoint metrics: request count, error count, latency distribution
- Cache metrics: hits, misses, hit ratio, evictions
- Database metrics: connection pool utilization, query latencies

**Log Shipping:**
- Filebeat integration for ELK stack
- Logs shipped from container stdout
- Correlation IDs enable full request tracing
- All logs searchable and correlatable by request

---

## Technology Stack

### Application Framework
- Flask 3.0+
- Gunicorn 21+ (4+ workers for production)

### Caching
- Redis 7.0+ (primary)
- In-memory cache for development fallback

### Persistence
- PostgreSQL 13+
- SQLAlchemy 2.0+ (ORM and query builder)
- Alembic 1.12+ (database migrations)

### Resilience
- tenacity 8.2+ (retry with exponential backoff)
- PyBreaker (circuit breaker pattern)
- requests 2.31+ (HTTP client with timeouts)

### Observability
- python-json-logger 2.0+ (JSON formatting)
- prometheus-client 0.17+ (metrics)

### DevOps & Deployment
- Docker 24+ (containerization)
- Docker Compose 2.20+ (local orchestration)
- Kubernetes 1.27+ / Minikube (production)
- Helm 3.12+ (Kubernetes packaging)
- Filebeat 8.10+ (log shipping)

---

## Deployment Options

### Local Development (Docker Compose)

```bash
docker compose up -d

Services:
- app (Flask on :5000)
- redis (cache on :6379)
- postgres (database on :5432)
- filebeat (logging)
```

### Production (Kubernetes / Minikube)

```bash
helm install rick-morty-api ./charts/rick-morty-api/

Deployed:
- Deployment: app (3 replicas, rolling updates)
- Service: LoadBalancer on :5000
- ConfigMap: Application configuration
- Secret: Database credentials
- PersistentVolumeClaim: PostgreSQL storage (20GB)
- StatefulSet: Redis (1 replica)
- DaemonSet: Filebeat (log collection)
```

**Health Probes:**
- Liveness: Pod restart on failure (timeout 5s, failures 3)
- Readiness: Remove from load balancer if unhealthy (timeout 10s, failures 2)
- Startup: Wait for database migration (timeout 30s)

---

## Success Criteria (Achieved)

- ✅ Cache hit ratio ≥ 80% for repeated queries within TTL window
- ✅ P99 latency for cached requests < 100ms
- ✅ Health check detects all critical dependencies within 5 seconds
- ✅ All requests/responses logged as JSON Lines to stdout + Filebeat
- ✅ 99.5% uptime sustained during validation period
- ✅ Rate limiting rejects >1000 req/min with 429 status
- ✅ Docker Compose and Helm deployments produce identical behavior
- ✅ Zero production hotfixes required in first 2 weeks post-launch

---

## Configuration Reference

All configuration loads from environment variables:

```bash
# Caching
CACHE_BACKEND=redis                 # or 'memory'
REDIS_URL=redis://localhost:6379/0
CACHE_SOCKET_TIMEOUT_S=5

# Persistence
DATABASE_URL=postgresql://user:pass@localhost:5432/rickmorty
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=15
DATABASE_QUERY_TIMEOUT_S=30
DATABASE_AUTO_MIGRATE=true

# Resilience
RETRY_ENABLED=true
RETRY_MAX_ATTEMPTS=5
RETRY_BASE_DELAY_MS=100
RETRY_MAX_DELAY_MS=30000
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RESET_TIMEOUT_S=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PUBLIC_TIER=100
RATE_LIMIT_STANDARD_TIER=1000
RATE_LIMIT_PREMIUM_TIER=5000

# Observability
LOG_LEVEL=INFO
CORRELATION_ID_HEADER=X-Correlation-ID
ENABLE_METRICS=true

# Application
FLASK_ENV=production
WORKERS=4
PORT=5000
```

---

## Failure Scenarios & Recovery

### Scenario 1: Redis Cache Unavailable
- Cache lookups timeout after 2s
- Application logs warning and continues
- Requests hit database then upstream API
- Performance degrades but functionality preserved
- Recovery: Automatic on Redis reconnection

### Scenario 2: PostgreSQL Connection Pool Exhausted
- New requests queue for up to 30s
- Successful connection → request proceeds
- Timeout → request fails with 503
- Health check reports degraded status
- Recovery: Wait for active queries to complete

### Scenario 3: Upstream API Rate Limited (429)
- Retry logic triggers with exponential backoff
- After 5 attempts (~30s delay), request fails
- Circuit breaker monitors failure rate
- If threshold exceeded → circuit opens (immediately reject)
- Recovery: Half-open probes after 60s

### Scenario 4: Upstream API Completely Down (503)
- Circuit breaker opens after 5 consecutive 503s
- Subsequent requests return 503 without calling API
- Clients get response from cache (even if expired) with stale flag
- Database provides fallback data
- Recovery: After 60s, circuit enters half-open, tries limited probes

---

## Monitoring & Alerting

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Cache hit ratio | > 80% | < 50% |
| Upstream API latency (p99) | < 500ms | > 1000ms |
| Request error rate | < 1% | > 5% |
| DB connection pool utilization | < 70% | > 80% |
| Circuit breaker OPEN duration | < 1m | > 10 minutes |
| Rate limit violations | < 10/min | > 100/min |
| Disk free space | > 20% | < 10% |
| Memory usage | < 70% | > 85% |

### Health Check Monitoring

- Monitor `/healthcheck` endpoint regularly
- Alert on status change to unhealthy/degraded
- Check individual dependency latencies
- Verify all Kubernetes probes passing

---

## Integration Notes

### With Existing Systems

1. **Upstream Rick & Morty API** - Integration point for character data
2. **Kubernetes Cluster** - Minikube for development, production-grade cluster for deployment
3. **Log Aggregation** - ELK stack (Elasticsearch, Logstash, Kibana) or OpenSearch
4. **Metrics Collection** - Prometheus + Grafana (optional but recommended)

### Data Migration Path

- Initial load: Sync all characters from upstream API on first startup
- Incremental sync: Background job runs hourly to sync changes
- Database represents source of truth for analytics
- Cache acts as performance layer

---

## Testing Coverage

- **Unit Tests**: > 90% coverage for cache, resilience, rate limit modules
- **Integration Tests**: Redis, PostgreSQL, upstream API interaction
- **End-to-End Tests**: Full stack with Docker Compose and Kubernetes
- **Performance Tests**: Load test (1000 req/sec), stress test, soak test
- **Chaos Tests**: Failure injection and recovery scenarios

---

## Operations Runbooks

### Common Issues & Resolution

**High latency despite cache:**
- Check cache hit ratio via `/metrics`
- Verify Redis connectivity and performance
- Review upstream API response times

**Rate limit false positives:**
- Check DDoS detection thresholds
- Verify API key consumer tier configuration
- Review spike detection logs

**Database connection exhaustion:**
- Scale connection pool size
- Check for slow queries in logs
- Monitor connection pool utilization

**Circuit breaker stuck OPEN:**
- Verify upstream API is responding
- Check circuit breaker reset timeout
- Consider manual reset if upstream recovered

---

## Archive & Change Tracking

This capability was formally archived from change `api-resilience-enhancement` on 2026-09-13.

**Original Change Artifacts:**
- Proposal: Comprehensive business justification and capabilities
- Design: Technical architecture and component design
- Specifications: 4 detailed specs (caching, persistence, resilience, observability)
- Tasks: 39 implementation tasks with acceptance criteria

All archived artifacts remain accessible in `openspec/changes/archive/api-resilience-enhancement/` for historical reference.

**Related Specs:**
- `01-caching.md` - Detailed caching layer specification
- `02-persistence.md` - Database schema and persistence design
- `03-resilience-ratelimit.md` - Resilience patterns and rate limiting
- `04-observability.md` - Logging, health checks, and monitoring

---

## Capability Ownership & Support

**Last Updated:** 2026-09-13  
**Maintained By:** Development Team  
**Questions:** Refer to archived change documentation or team wiki  

This specification defines the durable capability. Implementation teams should refer to this spec for feature requirements, configuration options, and operational guidance.
