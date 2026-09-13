# API Resilience Enhancement - Technical Design

## Architecture Overview

### System Diagram

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
        │                    Structured JSON Logging
        │                    (stdout → Filebeat → ELK)
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

### Data Flow: Request Lifecycle

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

## Component Architecture

### 1. Request Processing Layer

**Components:**
- `FlaskApplication`: Main routing and request handling
- `MiddlewareStack`: Correlation ID, rate limiting, CORS
- `RequestValidator`: Parameter validation and sanitization
- `ResponseFormatter`: Consistent response structure

**Key Patterns:**
- Middleware chain: Early failure (validation) before expensive operations
- Correlation ID: Injected at request boundary, propagated to all downstream systems
- Error handling: Try/catch at each layer, log with context, return appropriate status

**Code Structure:**
```python
# middleware/correlation_id.py
def correlation_id_middleware(f):
    """Inject correlation ID from header or generate new one"""
    @wraps(f)
    def decorated(*args, **kwargs):
        cid = request.headers.get('X-Correlation-ID')
        if not cid:
            cid = generate_correlation_id()
        g.correlation_id = cid
        logger.set_correlation_id(cid)
        response = make_response(f(*args, **kwargs))
        response.headers['X-Correlation-ID'] = cid
        return response
    return decorated
```

### 2. Caching Layer (Redis)

**Components:**
- `CacheBackend` (abstract): Interface for cache operations
- `RedisBackend`: Production Redis implementation
- `InMemoryBackend`: Development fallback
- `CacheDecorator`: Route-level caching decorator
- `CacheInvalidation`: TTL and manual invalidation

**Key Design Decisions:**

1. **Backend Abstraction**: Allows swapping Redis ↔ In-Memory without code changes
2. **Connection Pooling**: Pre-create Redis connections (10-20 pool size)
3. **Graceful Degradation**: Cache miss/timeout doesn't block response (serves from DB/API)
4. **Cache-Aside Pattern**: Application checks cache before data fetch
5. **TTL Strategy**: Different TTL for collections (300s) vs. individual items (3600s)

**Configuration:**
```python
# cache/backend.py
class RedisBackend:
    def __init__(self, url, pool_size=10, socket_timeout=5):
        self.pool = redis.ConnectionPool.from_url(
            url, 
            max_connections=pool_size,
            socket_timeout=socket_timeout
        )
        self.client = redis.Redis(connection_pool=self.pool)
        
    def get(self, key, default=None):
        try:
            value = self.client.get(key)
            return json.loads(value) if value else default
        except (ConnectionError, TimeoutError):
            logger.warning(f"Cache get failed for key={key}")
            return default
            
    def set(self, key, value, ttl_seconds=300):
        try:
            self.client.setex(key, ttl_seconds, json.dumps(value))
        except (ConnectionError, TimeoutError):
            logger.warning(f"Cache set failed for key={key}, ttl={ttl_seconds}")
```

### 3. Persistence Layer (PostgreSQL)

**Components:**
- `DatabaseConnection`: Connection pooling and lifecycle
- `CharacterRepository`: CRUD operations for characters
- `QueryResultRepository`: Store and retrieve query results
- `ApiCallRepository`: Audit trail of upstream calls
- `MetricsRepository`: Performance metrics aggregation
- `MigrationManager`: Alembic-based schema management

**Key Design Decisions:**

1. **Connection Pooling**: SQLAlchemy with 5-20 connection pool
2. **Repository Pattern**: Separate data access from business logic
3. **JSONB for Flexibility**: Store query_params and results as JSONB for complex queries
4. **Denormalization**: Store full character JSON for query efficiency
5. **Retention Policy**: Auto-delete old api_calls, metrics via scheduled job

**Schema Optimization:**
- `characters.id`: PRIMARY KEY (clustered index)
- `characters.(status, species, origin_name)`: Multi-column index for filtering
- `api_calls.correlation_id`: For request tracing
- `api_calls.created_at`: For retention policy and time-range queries
- `metrics.(endpoint, timestamp)`: For time-series queries

**Upsert Example:**
```python
# repository/character.py
def upsert_character(self, character_data):
    """Insert or update character, handling race conditions"""
    stmt = insert(Character).values(
        id=character_data['id'],
        name=character_data['name'],
        # ... other fields
        synced_at=datetime.utcnow()
    ).on_conflict_do_update(
        index_elements=['id'],
        set_={
            'name': character_data['name'],
            'updated_at': datetime.utcnow(),
            'synced_at': datetime.utcnow()
        }
    )
    return self.session.execute(stmt)
```

### 4. Resilience Layer

**Components:**
- `RetryPolicy`: Exponential backoff implementation
- `CircuitBreaker`: State machine (CLOSED → OPEN → HALF_OPEN)
- `TimeoutManager`: Timeout enforcement across layers
- `GracefulDegradation`: Fallback strategies

**Key Design Decisions:**

1. **Exponential Backoff Formula**: `delay = min(base * (2^n), max) * (1 ± jitter)`
2. **Circuit Breaker States**:
   - CLOSED: Requests pass through, count failures
   - OPEN: Requests rejected immediately after threshold
   - HALF_OPEN: Limited probe requests test recovery
3. **Timeout Hierarchy**: 
   - Socket timeout (TCP) < Read timeout (HTTP) < Total timeout (request)
4. **Graceful Fallback Order**: Cache → Database → Stale cache → Error

**Implementation:**
```python
# resilience/circuit_breaker.py
class CircuitBreaker:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    def __init__(self, failure_threshold=5, reset_timeout_s=60):
        self.state = self.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self.last_failure_time = None
        
    def call(self, func, *args, **kwargs):
        if self.state == self.OPEN:
            if self._should_attempt_reset():
                self.state = self.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            
    def _on_success(self):
        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
        self.failure_count = 0
```

### 5. Rate Limiting Layer

**Components:**
- `RateLimitMiddleware`: Intercept requests
- `RateLimitStore`: Redis-backed counter storage
- `ConsumerRegistry`: API key → tier mapping
- `RateLimitHeaders`: Response header generation
- `DDoSDetection`: Spike detection and mitigation

**Key Design Decisions:**

1. **Token Bucket Algorithm**: Refill at constant rate, reject if bucket empty
2. **Per-Consumer Tiers**: Public (100), Standard (1000), Premium (5000) req/min
3. **Storage**: Redis for fast counters (atomic increment)
4. **Precision**: 1-minute windows (reset on minute boundary)
5. **DDoS Detection**: Spike detection when single IP > 10x normal rate

**Algorithm:**
```python
# rate_limit/middleware.py
def check_rate_limit(consumer_id, limit_per_minute):
    """Check if consumer exceeded rate limit"""
    key = f"rate_limit:{consumer_id}:{current_minute()}"
    current_count = redis.incr(key)
    
    if current_count == 1:
        # First request this minute, set expiry
        redis.expire(key, 60)
    
    if current_count > limit_per_minute:
        reset_time = unix_timestamp_next_minute()
        retry_after_s = reset_time - time.time()
        
        return {
            'allowed': False,
            'remaining': 0,
            'reset_timestamp': reset_time,
            'retry_after_s': int(retry_after_s) + 1
        }
    
    return {
        'allowed': True,
        'remaining': limit_per_minute - current_count,
        'reset_timestamp': unix_timestamp_next_minute(),
        'retry_after_s': 0
    }
```

### 6. Observability Layer

**Components:**
- `StructuredLogger`: JSON formatter and correlation ID handling
- `RequestLogger`: Middleware to log all requests
- `PerformanceTracker`: Latency measurement at each layer
- `HealthCheckHandler`: Deep dependency checks
- `MetricsCollector`: Aggregate metrics (hit ratios, error rates)

**Key Design Decisions:**

1. **JSON Lines Format**: One valid JSON object per line for machine parsing
2. **Correlation ID Propagation**: Same ID through all logs/traces
3. **Sampling**: Optional log sampling for high-volume endpoints
4. **Structured Fields**: event_type, source_ip, latencies, context
5. **Performance Instrumentation**: Measure database_time, cache_time, upstream_time separately

**Health Check Logic:**
```python
# observability/health_check.py
def deep_health_check():
    """Check all critical dependencies"""
    checks = {}
    
    # Database check
    try:
        db.execute("SELECT 1")
        checks['database'] = {'status': 'healthy', 'latency_ms': 5}
    except Exception as e:
        checks['database'] = {'status': 'unhealthy', 'error': str(e)}
        
    # Cache check
    try:
        start = time.time()
        cache.ping()
        checks['cache'] = {'status': 'healthy', 'latency_ms': 2}
    except Exception as e:
        checks['cache'] = {'status': 'unhealthy', 'error': str(e)}
        
    # Overall determination
    critical_failures = [
        v for k, v in checks.items() 
        if k in ['database'] and v['status'] != 'healthy'
    ]
    
    return {
        'status': 'unhealthy' if critical_failures else 'healthy',
        'dependencies': checks
    }
```

## Technology Stack

### Application Framework
- **Flask 3.0+**: Lightweight, flexible Python web framework
- **Flask-CORS**: Cross-Origin Resource Sharing support
- **Gunicorn 21+**: Production WSGI server (4+ workers)

### Caching
- **Redis 7.0+**: High-performance cache backend
- **redis-py 5.0+**: Python Redis client with connection pooling
- **Fallback**: In-memory cache for development (using dict + TTL)

### Persistence
- **PostgreSQL 13+**: Relational database for durability
- **SQLAlchemy 2.0+**: ORM and query builder
- **Alembic 1.12+**: Database migration tool
- **psycopg3**: Python PostgreSQL driver with async support

### Resilience
- **tenacity 8.2+**: Retry decorator with exponential backoff
- **PyBreaker**: Circuit breaker pattern implementation
- **requests 2.31+**: HTTP client with timeout support

### Observability
- **python-json-logger 2.0+**: JSON logging formatter
- **python-structlog 23+**: Structured logging library (alternative)
- **prometheus-client 0.17+**: Metrics collection (for /metrics endpoint)

### DevOps & Deployment
- **Docker 24+**: Containerization
- **Docker Compose 2.20+**: Local orchestration
- **Kubernetes 1.27+**: Production orchestration (Minikube for testing)
- **Helm 3.12+**: Kubernetes package manager
- **Filebeat 8.10+**: Log shipping to ELK stack

### Testing
- **pytest 7.4+**: Test framework
- **pytest-cov**: Code coverage
- **pytest-mock**: Mocking fixtures
- **requests-mock**: Mock HTTP requests

## Deployment Architecture

### Local Development
```
docker-compose up -d

Services:
- app (Flask on :5000)
- redis (cache on :6379)
- postgres (database on :5432)
- filebeat (logging)
```

### Production (Minikube)
```
Helm deployment with:
- Deployment: app (3 replicas)
- Service: LoadBalancer on :5000
- ConfigMap: Application config
- Secret: Database credentials
- PersistentVolumeClaim: PostgreSQL storage
- Redis StatefulSet: 1 replica (no HA needed for this phase)
- Filebeat DaemonSet: Collect logs from all pods
```

### CI/CD Pipeline (GitHub Actions)
```
1. Push to main
2. Build Docker image: rick-morty-api:v1.0.0
3. Push to Docker Hub: username/rick-morty-api
4. Deploy to Minikube (if tests pass)
5. Run integration tests
6. Health check validation
```

## Failure Handling & Trade-offs

### Design Trade-offs

| Aspect | Decision | Rationale | Trade-off |
|--------|----------|-----------|-----------|
| Cache Backend | Redis primary, in-memory fallback | Production performance + dev simplicity | Fallback has limited size |
| Persistence | PostgreSQL denormalized schema | Query efficiency and analytical power | Increased storage vs. normalized |
| Retry Strategy | Exponential backoff with jitter | Prevents thundering herd | Slower recovery from failures |
| Circuit Breaker | 60s reset timeout | Balance between recovery and stability | May delay service recovery |
| Rate Limit Windows | Minute-based (not rolling) | Simpler implementation, Redis efficiency | Less smooth distribution |
| Logging | JSON Lines to stdout | Kubernetes-friendly, ELK ingestion | Higher log volume |
| Database Connections | 5-20 pool size | Reasonable concurrency without exhaustion | Requests may queue briefly |

### Failure Scenarios & Recovery

**Scenario 1: Redis Unavailable**
- Cache lookups timeout after 2s
- Application logs warning and continues
- Requests hit database then upstream API
- Performance degrades but functionality remains
- Recovery: Redis reconnection on next cycle

**Scenario 2: PostgreSQL Connection Pool Exhausted**
- New requests wait in queue for up to 30s
- If connection becomes available → request proceeds
- If timeout → request fails with 503
- Health check reports degraded status
- Recovery: Wait for active queries to complete, free connections

**Scenario 3: Upstream API Rate Limited (429)**
- Retry logic triggers with exponential backoff
- After 5 attempts (max ~30s delay), request fails
- Circuit breaker monitors failure rate
- If threshold exceeded → circuit opens (immediately reject)
- Recovery: Half-open probes after 60s

**Scenario 4: Upstream API Completely Down (503)**
- Circuit breaker opens after 5 consecutive 503s
- Subsequent requests immediately return 503 without calling API
- Clients get response from cache (even if expired) with stale flag
- Database provides fallback data
- Recovery: After 60s, circuit enters half-open, tries limited probes

## Security Considerations

1. **API Key Storage**: Store hashed API keys in database (bcrypt)
2. **Rate Limit Enforcement**: Prevent brute force and DoS
3. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)
4. **Sensitive Data**: Never log passwords, tokens, or PII in structured logs
5. **Correlation ID**: Used for audit trail, not security
6. **CORS**: Configurable via environment variable (restrict to known origins)
7. **Health Check**: May expose internal details, consider restricting to internal IPs

## Monitoring & Alerting

### Key Metrics to Track
- Cache hit ratio (target: > 80%)
- Upstream API latency (target: < 500ms p99)
- Request error rate (target: < 1%)
- Database connection pool utilization
- Circuit breaker state transitions
- Rate limit violation rate
- Disk space free percentage
- Memory usage percentage

### Alerting Thresholds
- Cache hit ratio < 50% → Investigate TTL or cache size
- Upstream latency > 1000ms p99 → Potential upstream degradation
- Error rate > 5% → Investigate failures
- Connection pool > 80% → Consider scaling
- Circuit breaker OPEN > 10 minutes → Upstream issue
- Rate limit violations > 100/min → Potential attack
- Disk free < 10% → Alert and auto-trigger cleanup
- Memory > 85% → Risk of OOM

## Testing Strategy

### Unit Tests
- Cache decorator: Hit, miss, expiration
- Retry logic: Backoff calculation, max attempts
- Circuit breaker: State transitions
- Rate limiter: Token bucket algorithm, tier enforcement
- Health checks: Dependency status detection

### Integration Tests
- Redis + application: Cache persistence and TTL
- PostgreSQL + application: Upsert, queries, connections
- Retry + upstream API: Transient failure recovery
- Circuit breaker + upstream: Cascading failure prevention
- Rate limiter + load: Concurrent request handling

### End-to-End Tests
- Docker Compose: Full stack deployment and verification
- Kubernetes + Minikube: Probe behavior, pod restart
- CI/CD pipeline: Build → test → deploy flow
- Failure injection: Chaos engineering tests

### Performance Tests
- Load test: 1000 req/sec with 80% cache hit
- Stress test: Connection pool exhaustion recovery
- Soak test: 24-hour run, memory stability
- Spike test: 10x normal load for 60 seconds

## Implementation Phases

### Phase 1: Caching Layer (Week 1)
- Redis integration
- Cache decorator
- Cache statistics
- Integration tests

### Phase 2: Persistence Layer (Week 2)
- Database schema
- Alembic migrations
- Repository pattern implementation
- Data sync logic

### Phase 3: Resilience (Week 3)
- Retry policy
- Circuit breaker
- Graceful degradation
- Timeout management

### Phase 4: Rate Limiting (Week 4)
- Rate limiter implementation
- API key management
- DDoS detection
- Rate limit headers

### Phase 5: Observability (Week 5)
- Structured JSON logging
- Health checks (deep, Kubernetes probes)
- Metrics collection
- Filebeat integration

### Phase 6: DevOps (Week 6)
- Docker Compose setup
- Helm charts
- GitHub Actions CI/CD
- Kubernetes deployment

### Phase 7: Testing & Tuning (Week 7)
- Comprehensive testing
- Performance tuning
- Documentation
- Team training
