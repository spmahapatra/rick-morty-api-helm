# Resilience & Rate Limiting Specification

## Feature: Resilience Patterns (Retry & Circuit Breaker)

### Functional Requirements

#### REQ-3.1: Exponential Backoff Retry Logic
Implement intelligent retry mechanism for transient failures.

**Retry Configuration:**
- Base delay: 100ms
- Max delay: 30 seconds
- Max retries: 5
- Jitter: ±20% random variation to prevent thundering herd
- Retry on: 429 (Too Many Requests), 503 (Service Unavailable), connection timeouts, socket errors

**Acceptance Criteria:**
- Transient failures succeed without user intervention
- Retry delays follow exponential backoff formula: `delay = min(base * (2^n), max_delay) * (1 ± jitter)`
- Logging clearly indicates retry attempts: `attempt: 1/5, next_retry_ms: 212`
- Non-retryable errors (400, 404) fail fast without retry

#### REQ-3.2: Circuit Breaker Pattern
Prevent cascading failures when upstream API is degraded.

**Circuit States:**
1. **CLOSED** (normal operation): Requests proceed, failures are counted
   - Failure threshold: 5 consecutive failures
   - Success threshold: 10 successful requests resets counter
2. **OPEN** (upstream unavailable): Requests rejected immediately
   - Duration: 60 seconds (after which moves to HALF_OPEN)
   - Error response: `503 Service Unavailable` with `Retry-After: 60`
3. **HALF_OPEN** (testing recovery): Limited probe requests allowed
   - Test requests: Max 3 per window
   - If 2+ succeed → move to CLOSED
   - If 1+ fail → move back to OPEN

**Acceptance Criteria:**
- Circuit breaker prevents 100+ rapid failures from hitting upstream
- State transitions are logged: `circuit_breaker_state_change: CLOSED -> OPEN`
- Health check reports circuit breaker status for monitoring

#### REQ-3.3: Timeout Management
Configurable timeouts at multiple layers.

- Socket timeout (TCP connection): 5 seconds
- Read timeout (waiting for response): 10 seconds
- Total request timeout: 20 seconds
- Database query timeout: 30 seconds
- Cache lookup timeout: 2 seconds
- Health check timeout: 15 seconds

**Acceptance Criteria:**
- All network operations have explicit timeouts
- Timeout exceeded → appropriate error status code
- Logs include timeout events: `operation: fetch_character, timeout_ms: 10000`

#### REQ-3.4: Graceful Degradation
Fallback behavior when primary systems fail.

- Cache unavailable → Serve from database if available
- Database unavailable → Return stale cache if within 6-hour window
- Both unavailable → Return 503 with `Retry-After` and cached data if exists
- Upstream API down → Serve database/cache with stale indicator header

**Acceptance Criteria:**
- Application never crashes due to downstream failure
- Users get partial response rather than complete failure
- Response headers indicate data freshness: `X-Data-Freshness: stale`

---

## Feature: Rate Limiting

### Functional Requirements

#### REQ-4.1: Endpoint-Level Rate Limiting
Limit requests per endpoint to prevent abuse.

**Default Limits:**
- `/characters`: 1000 requests/minute per IP
- `/characters/<id>`: 500 requests/minute per IP
- `/health`: 100 requests/minute per IP (prevent health check flooding)
- `/metrics`: 50 requests/minute (admin endpoint)

**Configuration:**
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STRATEGY=token_bucket  # or sliding_window
RATE_LIMIT_STORAGE=redis          # or memory
RATE_LIMIT_CLEANUP_INTERVAL=300   # seconds
```

**Acceptance Criteria:**
- Request counts are accurate within 1% per minute
- Limits reset on minute boundary (not rolling window)
- Requests over limit receive 429 status
- Rate limit headers included in response

#### REQ-4.2: Per-Consumer Rate Limiting
Support API key-based rate limiting for registered consumers.

**Consumer Tiers:**
- **Public** (no API key): 100 req/minute
- **Standard** (API key): 1000 req/minute
- **Premium** (API key + plan): 5000 req/minute
- **Enterprise**: Custom limits

**Implementation:**
- API key passed via header: `X-API-Key: <key>`
- Falls back to IP-based limiting if no key provided
- API key validation: Store in database, validate on each request

**Acceptance Criteria:**
- Different API keys can have different rate limits
- Rate limit enforcement is per-consumer (not global)
- Invalid/revoked API keys receive 401 Unauthorized

#### REQ-4.3: Rate Limit Response Headers
Include standard rate limit headers in all responses.

**Headers:**
```
RateLimit-Limit: 1000
RateLimit-Remaining: 987
RateLimit-Reset: 1694596320
Retry-After: 12
```

- `RateLimit-Limit`: Maximum allowed requests
- `RateLimit-Remaining`: Requests left in current window
- `RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying (if limited)

**Acceptance Criteria:**
- Headers present in all responses (success and limited)
- Headers accurately reflect current quota
- Consumers can use `Retry-After` for intelligent backoff

#### REQ-4.4: Rate Limit Metrics & Logging
Track rate limiting activity for monitoring and abuse detection.

**Metrics to track:**
- Rate limit violations per endpoint
- Rate limit violations per consumer/IP
- Top abusers (IPs/keys with most violations)
- Potential DDoS patterns (spike detection)

**Logging:**
- Log every violation: `rate_limit_exceeded: endpoint=/characters, ip=192.168.1.100, consumer_id=public`
- Aggregated metrics: Hourly summary of violations

**Acceptance Criteria:**
- Rate limit violations are observable via metrics endpoint
- Alerts can be configured on violation thresholds
- Historical data available for 30 days

---

## Feature: Resilience & Rate Limiting Scenarios

### Scenario 1: Retry on 503 Success
**Given** the Rick and Morty API returns 503 Service Unavailable on first request
**When** exponential backoff retry fires after 212ms
**Then** the second request succeeds with 200 OK
**And** response includes `X-Retry-Attempt: 2`
**And** total latency is ~220ms + upstream latency
**And** log shows: `retry_attempt: 2, final_status: 200`

### Scenario 2: Circuit Breaker Trips After Failures
**Given** the upstream API has been failing for 10 consecutive requests
**When** the 10th failure occurs
**Then** circuit breaker state changes to OPEN
**And** subsequent requests immediately return 503 (no upstream call)
**And** `Retry-After: 60` header indicates circuit will test recovery in 60s
**And** alert is triggered: "circuit_breaker_opened: rick_morty_api"

### Scenario 3: Circuit Breaker Half-Open Recovery
**Given** circuit breaker has been OPEN for 60 seconds
**When** time reaches 60 seconds and a request arrives
**Then** circuit moves to HALF_OPEN
**And** the request is forwarded as a probe
**And** if upstream succeeds, circuit returns to CLOSED
**And** log shows: `circuit_breaker_state_change: OPEN -> HALF_OPEN -> CLOSED`

### Scenario 4: Graceful Degradation - Cache Fallback
**Given** upstream API is down AND cache is available
**When** a client requests `/characters/1`
**Then** cached character data is returned
**And** response headers include `X-Cache-Status: stale, X-Data-Freshness: stale`
**And** response body includes `"stale_warning": "data is cached from 5 hours ago"`

### Scenario 5: Rate Limit - Public Consumer Exceeded
**Given** a public consumer (no API key) has made 100 requests in current minute
**When** request 101 arrives at `/characters`
**Then** response is 429 Too Many Requests
**And** headers show: `RateLimit-Limit: 100, RateLimit-Remaining: 0, Retry-After: 23`
**And** log entry: `rate_limit_exceeded: consumer=public, endpoint=/characters, ip=192.168.1.100`

### Scenario 6: Rate Limit - Premium Consumer Allowed
**Given** a Premium consumer (API key: sk_premium_xyz) has made 4500 requests in current minute
**When** request 4501 arrives with the Premium API key
**Then** response is 200 OK (within 5000 req/min limit)
**And** headers show: `RateLimit-Remaining: 499`
**And** request is logged as `consumer_tier: premium, quota_remaining: 499`

### Scenario 7: Rate Limit Reset Window
**Given** it is currently 10:05:30 (30 seconds into the minute)
**When** `/analytics/rate-limit-status` is queried
**Then** response shows: `reset_in_seconds: 30`
**And** at 10:06:00 all counters reset to their limit
**And** client can plan requests around reset windows

### Scenario 8: DDoS Pattern Detection
**Given** a single IP makes 50,000 requests in 1 minute
**When** the spike detection algorithm runs
**Then** IP is automatically rate-limited to 10 req/minute for 24 hours
**And** alert triggered: `potential_ddos: ip=203.0.113.5, requests_per_minute=50000`
**And** request source is logged for security investigation

---

## Non-Functional Requirements

| Requirement | Target | Priority |
|---|---|---|
| Retry success rate | 95% (transient failures succeed) | P0 |
| Circuit breaker response time | < 1ms (no downstream call) | P0 |
| Rate limit check latency | < 2ms | P1 |
| Rate limit accuracy | ±1% | P1 |
| Graceful degradation | Always return something vs. 500 error | P0 |
| Timeout enforcement | 100% of network operations | P0 |

---

## Configuration Requirements

```env
# Retry & Circuit Breaker
RETRY_ENABLED=true
RETRY_MAX_ATTEMPTS=5
RETRY_BASE_DELAY_MS=100
RETRY_MAX_DELAY_MS=30000
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RESET_TIMEOUT_S=60

# Timeouts
SOCKET_TIMEOUT_S=5
READ_TIMEOUT_S=10
TOTAL_REQUEST_TIMEOUT_S=20
DB_QUERY_TIMEOUT_S=30
CACHE_LOOKUP_TIMEOUT_S=2

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STRATEGY=token_bucket
RATE_LIMIT_STORAGE=redis
RATE_LIMIT_PUBLIC_PER_MINUTE=100
RATE_LIMIT_STANDARD_PER_MINUTE=1000
RATE_LIMIT_PREMIUM_PER_MINUTE=5000
RATE_LIMIT_DDOS_DETECTION_ENABLED=true
RATE_LIMIT_DDOS_THRESHOLD_PER_MINUTE=10000
```

---

## API Contract

### New Endpoints

#### GET /resilience-status
Current status of all resilience systems.
```
GET /resilience-status

Response: 200 OK
{
  "circuit_breaker": {
    "service": "rick_morty_api",
    "state": "CLOSED",
    "consecutive_failures": 0,
    "last_failure_at": "2024-09-13T10:15:32Z",
    "half_open_tests_passed": 12
  },
  "retry_policy": {
    "enabled": true,
    "max_attempts": 5,
    "success_rate": 0.98
  },
  "timeouts": {
    "socket_timeout_s": 5,
    "read_timeout_s": 10,
    "total_request_timeout_s": 20
  }
}
```

#### GET /rate-limit-status
Current rate limit status for requester.
```
GET /rate-limit-status
X-API-Key: sk_premium_xyz (optional)

Response: 200 OK
{
  "consumer_tier": "premium",
  "limit_per_minute": 5000,
  "current_minute_usage": 4523,
  "remaining": 477,
  "reset_in_seconds": 42,
  "requests_in_queue": 0
}
```

---

## Testing Requirements

- Unit tests for retry logic (success, max retries, backoff calculation)
- Integration tests for circuit breaker (state transitions, recovery)
- Failure injection tests: Simulate 503, 429, timeouts
- Load tests under rate limiting: Verify accurate enforcement
- DDoS simulation: Verify spike detection and mitigation
- Graceful degradation tests: Confirm fallback behavior

---

## Documentation

- Retry policy: When retries help vs. when they cause problems
- Circuit breaker: State machine diagram, tuning guidance
- Rate limiting: How to obtain API keys, tier benefits
- Troubleshooting: Common resilience issues and solutions
- Monitoring: Key metrics and alerting thresholds
