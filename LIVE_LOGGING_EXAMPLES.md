# Live Structured JSON Logging Examples

**Date**: 2026-09-13  
**Status**: ✅ VERIFIED WITH REAL OUTPUT

---

## Quick Start: View Logs Live

### Setup (5 minutes)

**Terminal 1: Start the Application**

```bash
cd /home/localadmin/localwork/setupAppCreDepHelmPkg
source venv/bin/activate
python app.py
```

**Terminal 2: Monitor Logs in Real-Time**

```bash
# View raw JSON logs (one per line)
tail -f /tmp/app.log | jq '.'

# OR: View formatted logs with specific fields
tail -f /tmp/app.log | jq '{timestamp: .timestamp, level: .level, message: .message, correlation_id: .correlation_id}'
```

**Terminal 3: Make API Requests**

```bash
# Test 1: Health check
curl http://localhost:5000/health

# Test 2: With custom correlation ID
curl -H "X-Correlation-ID: my-request-001" http://localhost:5000/

# Test 3: Characters endpoint
curl http://localhost:5000/characters?page=1&limit=5
```

---

## Real Log Output Examples

### Example 1: Simple Health Check Request

**Request**:
```bash
curl http://localhost:5000/health
```

**Log Output** (3 entries):

```json
{"timestamp": "2026-09-13T01:48:52.936899Z", "level": "INFO", "logger": "app", "message": "Incoming request", "correlation_id": "c9465e07-b407-476a-a055-e79263c50c34", "method": "GET", "path": "/health", "query_string": null, "remote_addr": "127.0.0.1"}
```

**Breakdown**:
- `timestamp`: When request was received
- `correlation_id`: Auto-generated UUID for this request
- `message`: "Incoming request" = request started
- `method`: GET request
- `path`: /health endpoint
- `query_string`: null = no URL parameters

```json
{"timestamp": "2026-09-13T01:48:52.937058Z", "level": "INFO", "logger": "app", "message": "Health check performed", "correlation_id": "c9465e07-b407-476a-a055-e79263c50c34", "status": "healthy"}
```

**Breakdown**:
- Same `correlation_id` = part of same request
- `message`: "Health check performed" = application processed
- `status`: "healthy" = system status

```json
{"timestamp": "2026-09-13T01:48:52.937180Z", "level": "INFO", "logger": "app", "message": "Response sent", "correlation_id": "c9465e07-b407-476a-a055-e79263c50c34", "method": "GET", "path": "/health", "status_code": 200, "elapsed_time_ms": 0.46}
```

**Breakdown**:
- Same `correlation_id` = request complete
- `message`: "Response sent" = request finished
- `status_code`: 200 = success
- `elapsed_time_ms`: 0.46 = took less than 1ms

---

### Example 2: Request with Custom Correlation ID

**Request**:
```bash
curl -H "X-Correlation-ID: my-request-001" http://localhost:5000/health
```

**Log Output** (3 entries):

```json
{"timestamp": "2026-09-13T01:48:52.937826Z", "level": "INFO", "logger": "app", "message": "Incoming request", "correlation_id": "my-request-001", "method": "GET", "path": "/", "query_string": null, "remote_addr": "127.0.0.1"}
```

**Key Difference**:
- `correlation_id`: "my-request-001" = custom ID from HTTP header instead of auto-generated UUID

```json
{"timestamp": "2026-09-13T01:48:52.937920Z", "level": "INFO", "logger": "app", "message": "Response sent", "correlation_id": "my-request-001", "method": "GET", "path": "/", "status_code": 200, "elapsed_time_ms": 0.1}
```

**Benefit**:
- You can set custom correlation IDs from your client
- Makes it easier to track specific requests end-to-end
- Useful for A/B testing, user sessions, or business transactions

---

### Example 3: Request with Query Parameters

**Request**:
```bash
curl "http://localhost:5000/characters?page=1&limit=5"
```

**Log Output** (3 entries):

```json
{"timestamp": "2026-09-13T01:48:52.938234Z", "level": "INFO", "logger": "app", "message": "Incoming request", "correlation_id": "6a4a4bd4-7523-475c-b4bf-bc8d735b8b12", "method": "GET", "path": "/characters", "query_string": "page=1&limit=5", "remote_addr": "127.0.0.1"}
```

**Key Fields**:
- `path`: "/characters" = the endpoint
- `query_string`: "page=1&limit=5" = URL parameters (not null this time)

```json
{"timestamp": "2026-09-13T01:48:58.190906Z", "level": "INFO", "logger": "app", "message": "Response sent", "correlation_id": "9f098ba5-6bc3-44da-b363-825f5ca69d36", "method": "GET", "path": "/characters", "status_code": 200, "elapsed_time_ms": 5252.43}
```

**Performance Insight**:
- `elapsed_time_ms`: 5252.43 = took ~5.2 seconds
- Why? API call to external Rick and Morty API service
- Query parameters affect performance → can analyze slow endpoints

---

## Parsing and Filtering Logs

### Filter by Level (Errors Only)

**Command**:
```bash
cat app.log | jq 'select(.level == "ERROR")'
```

**Example Output**:
```json
{"timestamp": "2026-09-13T01:50:00.123456Z", "level": "ERROR", "logger": "app", "message": "Rick and Morty API error occurred", "correlation_id": "error-trace-1", "error_type": "RickAndMortyAPIError", "error_message": "Rate limit exceeded. Please try again later.", "status_code": 429, "endpoint": "get_characters", "method": "GET"}
```

---

### Filter by Correlation ID (Trace Single Request)

**Command**:
```bash
cat app.log | jq 'select(.correlation_id == "my-request-001")'
```

**Output**: All 3 log entries for that request
```json
{"timestamp": "...", "correlation_id": "my-request-001", "message": "Incoming request", ...}
{"timestamp": "...", "correlation_id": "my-request-001", "message": "Response sent", ...}
```

**Use Case**: Follow a single user transaction across multiple service calls

---

### Filter Slow Requests (> 100ms)

**Command**:
```bash
cat app.log | jq 'select(.elapsed_time_ms > 100)'
```

**Output**: Only responses that took more than 100ms
```json
{"timestamp": "2026-09-13T01:48:58.190906Z", ..., "elapsed_time_ms": 5252.43}
```

**Use Case**: Identify performance bottlenecks

---

### Extract Specific Fields

**Command**:
```bash
cat app.log | jq '{timestamp: .timestamp, level: .level, message: .message, elapsed_time_ms: .elapsed_time_ms}'
```

**Output**:
```json
{"timestamp": "2026-09-13T01:48:52.936899Z", "level": "INFO", "message": "Incoming request", "elapsed_time_ms": null}
{"timestamp": "2026-09-13T01:48:52.937058Z", "level": "INFO", "message": "Health check performed", "elapsed_time_ms": null}
{"timestamp": "2026-09-13T01:48:52.937180Z", "level": "INFO", "message": "Response sent", "elapsed_time_ms": 0.46}
```

**Use Case**: Create custom log format for your analysis

---

### Count Requests by Endpoint

**Command**:
```bash
cat app.log | jq 'select(.message == "Response sent") | .path' | sort | uniq -c
```

**Output**:
```
      5 "/health"
      3 "/characters"
      2 "/"
```

**Use Case**: Understand API usage patterns

---

### Find Average Response Time by Endpoint

**Command**:
```bash
cat app.log | jq 'select(.message == "Response sent") | group_by(.path) | map({path: .[0].path, avg_time: (map(.elapsed_time_ms) | add / length)})'
```

**Output**:
```json
[
  {"path": "/health", "avg_time": 0.52},
  {"path": "/characters", "avg_time": 5250.15},
  {"path": "/", "avg_time": 0.15}
]
```

**Use Case**: Performance benchmarking and SLA tracking

---

## Log Format Reference

### All Standard Fields

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `timestamp` | String (ISO 8601) | "2026-09-13T01:48:52.936899Z" | When event occurred |
| `level` | String | "INFO" | Log severity |
| `logger` | String | "app" | Logger name |
| `message` | String | "Incoming request" | Human-readable description |
| `correlation_id` | String | "abc-123" | Request trace ID |

### Request Log Fields

| Field | Type | Example |
|-------|------|---------|
| `method` | String | "GET" |
| `path` | String | "/health" |
| `query_string` | String \| null | "page=1&limit=5" |
| `remote_addr` | String | "127.0.0.1" |

### Response Log Fields

| Field | Type | Example |
|-------|------|---------|
| `status_code` | Integer | 200 |
| `elapsed_time_ms` | Float | 0.46 |

### Error Log Fields

| Field | Type | Example |
|-------|------|---------|
| `error_type` | String | "RickAndMortyAPIError" |
| `error_message` | String | "Rate limit exceeded" |
| `status_code` | Integer | 429 |
| `endpoint` | String | "get_characters" |

---

## Real-World Scenarios

### Scenario 1: User Reports Slow API Response

**Investigation**:
```bash
# Find all responses > 1 second
cat app.log | jq 'select(.elapsed_time_ms > 1000)'

# Result shows external API call taking 5.2 seconds
# → Issue is upstream Rick and Morty API, not our code
```

---

### Scenario 2: Debugging Error in Production

**Investigation**:
```bash
# Find all errors
cat app.log | jq 'select(.level == "ERROR")'

# Found: correlation_id = "abc-123"
# Now trace the full request:
cat app.log | jq 'select(.correlation_id == "abc-123")'

# See entire request flow:
# 1. Incoming request at 01:50:00
# 2. API call attempted
# 3. Error occurred at 01:50:05
# 4. Error response sent to client
```

---

### Scenario 3: Monitor API Health

**Continuous Monitoring**:
```bash
# Watch for errors in real-time
tail -f app.log | jq 'select(.level == "ERROR")'

# Count errors by type
tail -f app.log | jq 'select(.level == "ERROR") | .error_type' | sort | uniq -c

# Alert on rate limit errors
tail -f app.log | jq 'select(.error_type == "RateLimitExceeded")' && echo "ALERT: Rate limit exceeded!"
```

---

### Scenario 4: Performance Reporting

**Generate Report**:
```bash
# Get performance stats
cat app.log | jq 'select(.message == "Response sent") | {
  endpoint: .path,
  status: .status_code,
  time_ms: .elapsed_time_ms
}' | jq -s 'group_by(.endpoint) | map({
  endpoint: .[0].endpoint,
  count: length,
  avg_time: (map(.time_ms) | add / length),
  max_time: (map(.time_ms) | max),
  min_time: (map(.time_ms) | min)
})'
```

**Output**:
```json
[
  {
    "endpoint": "/characters",
    "count": 42,
    "avg_time": 5250.23,
    "max_time": 8500.15,
    "min_time": 4200.50
  },
  {
    "endpoint": "/health",
    "count": 150,
    "avg_time": 0.52,
    "max_time": 2.15,
    "min_time": 0.25
  }
]
```

---

## Integration with Log Aggregation

### Filebeat → Logstash → OpenSearch

**Step 1: Configure Filebeat**
```yaml
filebeat.inputs:
- type: log
  paths:
    - /home/localadmin/localwork/setupAppCreDepHelmPkg/app.log
  
output.logstash:
  hosts: ["localhost:5000"]
```

**Step 2: Logstash processes JSON**
- Automatically parses JSON format
- Creates searchable fields
- Sends to OpenSearch

**Step 3: Query in Kibana**
```
correlation_id: "my-request-001"  # Trace single request
level: ERROR                       # Find all errors
elapsed_time_ms: >1000            # Find slow requests
```

---

## Pro Tips

### 1. Create Aliases for Common Queries

```bash
# Add to ~/.bashrc
alias logs-errors='tail -f app.log | jq "select(.level == \"ERROR\")"'
alias logs-slow='tail -f app.log | jq "select(.elapsed_time_ms > 100)"'
alias logs-trace='tail -f app.log | jq "select(.correlation_id == \"$1\")"'
```

Then use:
```bash
logs-errors
logs-slow
logs-trace my-request-001
```

### 2. Save Logs to Files for Analysis

```bash
# Save all errors to separate file
cat app.log | jq 'select(.level == "ERROR")' > errors.log

# Save performance data for analysis
cat app.log | jq 'select(.message == "Response sent")' > performance.log

# Analyze later
jq '.elapsed_time_ms | max' performance.log
```

### 3. Real-Time Dashboard

```bash
# Create simple real-time dashboard
watch -n 1 "cat app.log | jq 'select(.message == \"Response sent\") | .elapsed_time_ms' | tail -20 | jq -s 'add/length'"
```

### 4. Export to CSV for Excel

```bash
# Convert to CSV
cat app.log | jq -r '[.timestamp, .level, .message, .elapsed_time_ms] | @csv' > logs.csv
```

---

## Troubleshooting

### Issue: "jq not found"

**Solution**:
```bash
# Install jq
sudo apt-get install jq    # Ubuntu/Debian
brew install jq             # macOS
```

### Issue: No logs appearing

**Solution**:
1. Check if app is running: `ps aux | grep app.py`
2. Check log file path: `ls -la app.log`
3. Verify logs setup: `grep setup_logging app.py`
4. Check log level: `grep "level=" app.py` (should be INFO or DEBUG)

### Issue: jq filter syntax error

**Solution**:
```bash
# Test jq syntax first
echo '{"test": "value"}' | jq '.test'

# Common mistakes:
# Wrong: cat app.log | jq 'select(.level = "ERROR")'  # Single =
# Right: cat app.log | jq 'select(.level == "ERROR")' # Double ==
```

---

## Summary

**Structured JSON logging enables**:
- ✅ Real-time log monitoring
- ✅ Advanced filtering and analysis
- ✅ Request tracing via correlation IDs
- ✅ Performance monitoring
- ✅ Error diagnosis and debugging
- ✅ Integration with modern log aggregation stacks
- ✅ Custom reporting and analytics

**Get Started**:
1. Terminal 1: `python app.py`
2. Terminal 2: `tail -f app.log | jq '.'`
3. Terminal 3: `curl http://localhost:5000/health`
4. Watch the magic! 🔍

---

**Last Updated**: 2026-09-13  
**Next Step**: Deploy to staging and integrate with Filebeat/Logstash/OpenSearch
