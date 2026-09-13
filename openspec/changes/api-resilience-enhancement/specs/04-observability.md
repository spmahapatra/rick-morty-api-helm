# Observability & Health Specification

## Feature: Structured Logging & JSON Output

### Functional Requirements

#### REQ-5.1: JSON Lines Logging Format
Implement structured JSON logging for machine parsing and analysis.

**Log Format:**
Each line is valid JSON with the following structure:
```json
{
  "timestamp": "2024-09-13T10:15:32.456789Z",
  "level": "INFO",
  "correlation_id": "req_abc123def456",
  "service": "rick-morty-api",
  "version": "1.0.0",
  "message": "Character fetched successfully",
  "event_type": "character_fetch",
  "endpoint": "/characters/1",
  "method": "GET",
  "request_id": "req_abc123def456",
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "http_status_code": 200,
  "response_time_ms": 45,
  "cache_hit": true,
  "cache_backend": "redis",
  "database_query_time_ms": 0,
  "upstream_api_time_ms": 0,
  "error_code": null,
  "error_message": null,
  "stacktrace": null,
  "context": {
    "character_id": 1,
    "page": 1,
    "limit": 10,
    "cache_ttl_remaining_s": 287
  }
}
```

**Field Definitions:**
- `timestamp`: ISO 8601 UTC timestamp
- `level`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `correlation_id`: Unique ID for tracing request through system
- `service`: Application name for multi-service deployments
- `version`: Semantic version of application
- `message`: Human-readable log message
- `event_type`: Structured event category (character_fetch, cache_miss, retry_attempt, etc.)
- `endpoint`: HTTP endpoint being called
- `method`: HTTP method (GET, POST, etc.)
- `request_id`: Unique request ID (same as correlation_id for ingress)
- `source_ip`: Client IP address
- `user_agent`: Client user agent string
- `http_status_code`: Response HTTP status
- `response_time_ms`: Total request processing time
- `cache_hit`: Boolean indicating cache hit
- `cache_backend`: Which cache backend was used
- `database_query_time_ms`: Time spent in database queries
- `upstream_api_time_ms`: Time spent calling upstream API
- `error_code`: Application error code (not HTTP status)
- `error_message`: Description of error
- `stacktrace`: Full stack trace for errors (null for success)
- `context`: Additional contextual fields specific to event

**Acceptance Criteria:**
- All logs are valid JSON on each line (JSON Lines format)
- No log line exceeds 10KB
- Logs include all required fields
- Logs output to stdout for container/Kubernetes collection

#### REQ-5.2: Correlation ID Propagation
Enable request tracing across distributed systems.

**Correlation ID:**
- Generated once per ingress request (if not provided)
- Format: `{service}_{timestamp}_{random_id}` (e.g., `api_20240913_101532_abc123`)
- Passed via header: `X-Correlation-ID` in upstream requests
- Included in all logs for that request
- Stored in database for audit trail

**Acceptance Criteria:**
- Every request gets a unique correlation ID
- ID is preserved across all service boundaries
- ID enables complete request tracing from client to upstream API
- Logs can be queried by correlation_id to see full request lifecycle

#### REQ-5.3: Log Level Configuration
Configurable verbosity for different environments.

**Log Levels:**
- `CRITICAL`: Application failures, data corruption, security issues
- `ERROR`: Request failures, external service errors
- `WARNING`: Degraded performance, retries, rate limits
- `INFO`: Request summaries, cache decisions, state changes
- `DEBUG`: Detailed execution flow, function parameters (dev/staging only)

**Configuration:**
```env
LOG_LEVEL=INFO                    # Default: INFO
LOG_LEVEL_OVERRIDE_MODULE=debug   # Override for specific modules
LOG_FORMAT=json                    # json or text
LOG_OUTPUT=stdout                 # stdout or file://path
LOG_SAMPLING_RATE=1.0            # 1.0 = all, 0.1 = 10%
```

**Acceptance Criteria:**
- Production uses INFO by default (minimal verbose output)
- DEBUG logging can be enabled temporarily without restart
- High-volume endpoints can use sampling to reduce log volume

#### REQ-5.4: Performance Metrics Logging
Log performance data for monitoring and alerting.

**Key Metrics to Log:**
- Request latency (p50, p95, p99)
- Cache hit/miss ratio
- Database connection pool utilization
- Upstream API response times
- Error rates by endpoint
- Rate limit violation rate

**Per-Request Logging:**
- `response_time_ms`: Total elapsed time
- `database_query_time_ms`: Time in database (if applicable)
- `upstream_api_time_ms`: Time calling external API
- `cache_hit`: Whether result came from cache
- `cache_operation_ms`: Time to check/update cache

**Acceptance Criteria:**
- Performance metrics logged on every request
- Metrics enable SLI/SLO calculation
- Outliers (slow requests) trigger separate PERFORMANCE log event

#### REQ-5.5: Error Logging & Stack Traces
Comprehensive error logging for debugging.

**Error Log Structure:**
```json
{
  "level": "ERROR",
  "event_type": "upstream_api_error",
  "error_code": "UPSTREAM_503",
  "error_message": "Rick and Morty API returned 503 Service Unavailable",
  "http_status_code": 503,
  "retry_count": 2,
  "max_retries": 5,
  "next_retry_ms": 412,
  "stacktrace": "Traceback (most recent call last):\n  File \"app.py\", line 91...",
  "context": {
    "upstream_service": "rick_morty_api",
    "upstream_status_code": 503,
    "upstream_response_time_ms": 10023
  }
}
```

**Acceptance Criteria:**
- Stack traces captured for all exceptions
- Error context helps identify root cause
- Sensitive data (passwords, tokens) never logged
- Errors logged before propagating to client

---

## Feature: Deep Health Check Endpoint

### Functional Requirements

#### REQ-6.1: Comprehensive Health Endpoint
Implement `/healthcheck` endpoint with deep dependency checks.

**Endpoint Specification:**
```
GET /healthcheck
Accept: application/json
X-Health-Verbose: true (optional, for extended diagnostics)

Response: 200 OK (healthy) or 503 Service Unavailable (unhealthy)
{
  "status": "healthy",  # or "degraded" or "unhealthy"
  "timestamp": "2024-09-13T10:15:32.456789Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "dependencies": {
    "database": {
      "status": "healthy",
      "latency_ms": 12,
      "checked_at": "2024-09-13T10:15:32Z",
      "details": {
        "pool_size": 10,
        "active_connections": 3,
        "idle_connections": 7,
        "connection_timeout_s": 30,
        "last_connection_error": null
      }
    },
    "cache": {
      "status": "healthy",
      "latency_ms": 5,
      "checked_at": "2024-09-13T10:15:32Z",
      "details": {
        "backend": "redis",
        "memory_bytes": 45000000,
        "keys_count": 1234,
        "eviction_policy": "allkeys-lru",
        "hit_ratio": 0.87,
        "last_error": null
      }
    },
    "upstream_api": {
      "status": "healthy",
      "latency_ms": 145,
      "checked_at": "2024-09-13T10:15:32Z",
      "details": {
        "service": "rick_morty_api",
        "circuit_breaker_state": "CLOSED",
        "consecutive_failures": 0,
        "last_check_time_ms": 145,
        "last_failure_at": null
      }
    },
    "disk_space": {
      "status": "healthy",
      "usage_percent": 45,
      "free_gb": 150,
      "threshold_percent": 80
    },
    "memory": {
      "status": "healthy",
      "usage_percent": 32,
      "available_mb": 2048,
      "threshold_percent": 85
    },
    "filebeat": {
      "status": "healthy",
      "latency_ms": 8,
      "checked_at": "2024-09-13T10:15:32Z",
      "details": {
        "last_heartbeat_s_ago": 2,
        "events_processed": 45000,
        "events_dropped": 0
      }
    }
  },
  "checks_performed": 6,
  "checks_passed": 6,
  "checks_failed": 0,
  "checks_degraded": 0,
  "overall_status": "healthy",
  "recommendations": []
}
```

**Dependencies to Check:**
1. **Database**: Can connect, query, get schema version
2. **Cache**: Can connect, ping, get stats
3. **Upstream API**: Can reach, measure latency
4. **Disk Space**: Monitor free space, alert if < 20%
5. **Memory**: Monitor heap usage, alert if > 85%
6. **Logging**: Filebeat connection status, event throughput

**Acceptance Criteria:**
- All 6 dependencies have individual health status
- Overall status is "healthy" only if all critical dependencies are healthy
- "degraded" if non-critical services fail
- "unhealthy" if database or upstream API unreachable
- Health check completes within 15 seconds
- Each dependency has latency < 5 seconds

#### REQ-6.2: Kubernetes Liveness & Readiness Probes
Support Kubernetes-native health checking.

**Liveness Probe** (`/health/live`):
- Checks: Application process is alive (memory, CPU not exhausted)
- Frequency: Every 10 seconds
- Timeout: 5 seconds
- Failure threshold: 3 consecutive failures → pod restart
- Response: `200 OK` if process is healthy

**Readiness Probe** (`/health/ready`):
- Checks: All critical dependencies are healthy
- Frequency: Every 5 seconds
- Timeout: 10 seconds
- Failure threshold: 2 consecutive failures → remove from load balancer
- Response: `200 OK` only if database + cache + upstream API reachable
- Response: `503 Service Unavailable` if any critical dependency down

**Startup Probe** (`/health/startup`):
- Checks: Database migrations completed, cache initialized
- Frequency: Every 5 seconds
- Timeout: 30 seconds
- Deadline: 5 minutes to complete startup checks
- Response: `200 OK` when ready to serve traffic

**Acceptance Criteria:**
- Kubernetes can use probes to determine pod health
- Failing pod is automatically restarted
- Pod is removed from load balancer if dependencies fail
- Startup probe prevents traffic until initialized

---

## Feature: Structured Logging Scenarios

### Scenario 1: Successful Request Logged
**Given** a client calls `GET /characters/1`
**When** the request succeeds with 200 OK
**Then** a JSON log entry is written with:
- `level: INFO`
- `event_type: character_fetch`
- `http_status_code: 200`
- `response_time_ms: 45`
- `cache_hit: true`
- `correlation_id: req_abc123def456` (unique per request)

### Scenario 2: Error Logged with Stack Trace
**Given** the database connection fails unexpectedly
**When** the next request tries to query
**Then** a JSON log entry is written with:
- `level: ERROR`
- `event_type: database_connection_failed`
- `error_code: DB_CONNECTION_ERROR`
- `error_message: "Connection refused: 127.0.0.1:5432"`
- `stacktrace: <full Python traceback>`
- `http_status_code: 503`

### Scenario 3: Request Tracing Across Systems
**Given** a client includes header: `X-Correlation-ID: trace_001`
**When** the request is processed
**Then** all downstream calls (database, cache, upstream API) use same correlation_id
**And** logs can be queried: `grep "trace_001" application.log | jq` to see full lifecycle
**And** Filebeat/ELK can correlate all events from that trace

### Scenario 4: Performance Outlier Detection
**Given** a request normally takes 45ms
**When** a request takes 2500ms (50x slower)
**Then** a separate log event is triggered:
- `level: WARNING`
- `event_type: slow_request_detected`
- `response_time_ms: 2500`
- `expected_p99_ms: 500`
- `excess_ms: 2000`
- Log helps operations identify performance regressions

### Scenario 5: DEBUG Logging in Development
**Given** developer sets `LOG_LEVEL=DEBUG`
**When** requests are processed
**Then** detailed logs show:
- Function entry/exit: `event_type: function_enter, function: fetch_characters`
- Parameter values: `params: {page: 1, limit: 10}`
- Internal state: `cache_backend_selected: redis`
- Execution details: `operation: cache_lookup_started`

### Scenario 6: Log Sampling for High-Volume Endpoints
**Given** `/characters` endpoint gets 100 req/sec
**And** `LOG_SAMPLING_RATE=0.1` (sample 10%)
**When** logging operates
**Then** approximately 10 req/sec are logged
**And** sampled logs are still valid JSON
**And** sampling ratio is recorded in logs: `sampled: true, sampling_rate: 0.1`

---

## Feature: Health Check Scenarios

### Scenario 1: Healthy Application
**Given** all dependencies are working
**When** `GET /healthcheck` is called
**Then** response is 200 OK
**And** `status: healthy`
**And** all 6 dependency checks show status: healthy
**And** `checks_passed: 6, checks_failed: 0`

### Scenario 2: Degraded: Cache Unavailable
**Given** Redis is disconnected
**But** database and upstream API are working
**When** `GET /healthcheck` is called
**Then** response is 200 OK
**And** `status: degraded` (cache is non-critical)
**And** `dependencies.cache.status: unhealthy`
**And** `dependencies.cache.last_error: "Connection refused"`
**And** `checks_degraded: 1` 

### Scenario 3: Unhealthy: Database Down
**Given** PostgreSQL is unreachable
**When** `GET /healthcheck` is called
**Then** response is 503 Service Unavailable
**And** `status: unhealthy` (database is critical)
**And** `dependencies.database.status: unhealthy`
**And** Kubernetes readiness probe fails → pod removed from load balancer

### Scenario 4: Kubernetes Liveness Probe
**Given** Kubernetes is configured with liveness probe: `GET /health/live`
**When** application is running
**Then** probe receives 200 OK
**And** pod continues running
**When** application process crashes
**Then** probe receives timeout/connection refused
**And** after 3 failures, Kubernetes restarts the pod

### Scenario 5: Kubernetes Readiness Probe
**Given** database is starting up (migration in progress)
**When** readiness probe queries `/health/ready`
**Then** response is 503 Service Unavailable
**And** Kubernetes doesn't route traffic to this pod
**When** database migration completes
**Then** readiness probe receives 200 OK
**And** Kubernetes starts routing traffic to pod

### Scenario 6: Startup Probe for Database Migrations
**Given** application is starting (Pod is creating)
**When** startup probe queries `/health/startup`
**Then** response is 503 while migrations run
**And** after migrations complete and cache warming, response is 200 OK
**And** readiness probes start passing
**And** pod enters ready state

### Scenario 7: Health Check Provides Diagnostic Info
**Given** an operator is troubleshooting slow performance
**When** `/healthcheck?verbose=true` is called
**Then** response includes:
- Upstream API latency: 850ms (slow)
- Circuit breaker state: HALF_OPEN (recovering from failure)
- Cache hit ratio: 0.42 (low)
- Database active connections: 18/20 (nearly exhausted)
- Disk space: 12% free (warning)
- Recommendations: ["Clear cache to free memory", "Add more database connections"]

---

## Non-Functional Requirements

| Requirement | Target | Priority |
|---|---|---|
| Health check latency | < 15 seconds | P0 |
| Database check latency | < 5 seconds | P1 |
| Log volume | < 100KB/sec normal load | P1 |
| Log ingestion latency | < 2 seconds to ELK | P2 |
| Correlation ID accuracy | 100% of requests | P0 |
| Health check accuracy | 100% (no false positives) | P0 |

---

## Configuration Requirements

```env
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_OUTPUT=stdout
LOG_SAMPLING_RATE=1.0
CORRELATION_ID_HEADER=X-Correlation-ID
LOG_MAX_LINE_SIZE=10000

# Health Checks
HEALTHCHECK_TIMEOUT_S=15
DATABASE_CHECK_TIMEOUT_S=5
CACHE_CHECK_TIMEOUT_S=5
UPSTREAM_API_CHECK_TIMEOUT_S=10
DISK_SPACE_THRESHOLD_PERCENT=20
MEMORY_THRESHOLD_PERCENT=85
FILEBEAT_CHECK_TIMEOUT_S=5

# Kubernetes Probes
LIVENESS_PROBE_INTERVAL_S=10
READINESS_PROBE_INTERVAL_S=5
STARTUP_PROBE_INTERVAL_S=5
STARTUP_PROBE_DEADLINE_S=300
```

---

## API Contract

### New Endpoints

#### GET /health
Simple health check (backward compatible).
```
GET /health

Response: 200 OK
{
  "status": "healthy"
}
```

#### GET /healthcheck
Deep health check with dependency details.
```
GET /healthcheck?verbose=true

Response: 200 OK or 503 Service Unavailable
{
  "status": "healthy|degraded|unhealthy",
  "dependencies": {...},
  "checks_passed": 6,
  "checks_failed": 0
}
```

#### GET /health/live
Kubernetes liveness probe endpoint.
```
GET /health/live

Response: 200 OK (application alive)
{
  "status": "alive"
}
```

#### GET /health/ready
Kubernetes readiness probe endpoint.
```
GET /health/ready

Response: 200 OK or 503 Service Unavailable
{
  "status": "ready|not_ready",
  "reason": "ready to serve traffic" or "database unavailable"
}
```

#### GET /health/startup
Kubernetes startup probe endpoint.
```
GET /health/startup

Response: 200 OK or 503 Service Unavailable
{
  "status": "started|starting",
  "migrations_completed": true,
  "cache_warmed": true
}
```

---

## Testing Requirements

- Unit tests for log formatting (valid JSON structure)
- Integration tests for health checks (all dependencies)
- Kubernetes probe tests: Verify probe behavior on failure scenarios
- Correlation ID propagation: Verify ID across all layers
- Performance under logging: Verify < 100KB/sec at load
- ELK integration: Verify logs ingested and searchable

---

## Documentation

- Logging format specification and field meanings
- Health check interpretation guide
- Kubernetes probe configuration examples
- ELK stack setup and log querying
- Troubleshooting using structured logs and correlation IDs
