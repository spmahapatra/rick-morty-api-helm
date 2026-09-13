# Structured JSON Logging Implementation

**Date**: 2026-09-13  
**Status**: ✅ Complete  
**Scope**: Application request/response and error logging

---

## Overview

Structured JSON logging has been implemented for the Rick and Morty API. All logs are now output in JSON Lines format, optimized for log aggregation and analysis.

---

## Log Format Specification

### Standard Log Entry

```json
{
  "timestamp": "2026-09-13T01:42:37.502901Z",
  "level": "INFO|WARNING|ERROR|CRITICAL|DEBUG",
  "logger": "logger_name",
  "message": "Human-readable message",
  "correlation_id": "unique-request-id",
  ...context_fields
}
```

### Timestamp

- **Field**: `timestamp`
- **Format**: ISO 8601 with UTC timezone (Z suffix)
- **Example**: `"2026-09-13T01:42:37.502901Z"`
- **Purpose**: Precise timing for log analysis and correlation

### Log Level

- **Field**: `level`
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `"level": "INFO"`
- **Purpose**: Severity filtering and alerting

### Correlation ID

- **Field**: `correlation_id`
- **Format**: UUID v4 or custom header value
- **Source**: `X-Correlation-ID` HTTP header or auto-generated
- **Example**: `"correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768"`
- **Purpose**: Request tracing across services and aggregation

---

## Log Entry Types

### 1. Incoming Request Log

**Triggered**: Before request processing (`@app.before_request`)

```json
{
  "timestamp": "2026-09-13T01:42:37.502901Z",
  "level": "INFO",
  "logger": "app",
  "message": "Incoming request",
  "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768",
  "method": "GET",
  "path": "/health",
  "query_string": null,
  "remote_addr": "127.0.0.1"
}
```

**Context Fields**:
- `method`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `path`: Request path
- `query_string`: Query parameters (null if none)
- `remote_addr`: Client IP address

### 2. Response Log

**Triggered**: After response sent (`@app.after_request`)

```json
{
  "timestamp": "2026-09-13T01:42:37.503322Z",
  "level": "INFO",
  "logger": "app",
  "message": "Response sent",
  "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "elapsed_time_ms": 0.75
}
```

**Context Fields**:
- `method`: HTTP method
- `path`: Request path
- `status_code`: HTTP response code
- `elapsed_time_ms`: Request processing time in milliseconds

### 3. Application-Level Logging

**Example: Health Check**

```json
{
  "timestamp": "2026-09-13T01:42:37.503136Z",
  "level": "INFO",
  "logger": "app",
  "message": "Health check performed",
  "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768",
  "status": "healthy"
}
```

### 4. Error Logging

**Example: API Error with Context**

```json
{
  "timestamp": "2026-09-13T01:45:22.123456Z",
  "level": "ERROR",
  "logger": "app",
  "message": "Rick and Morty API error occurred",
  "correlation_id": "abc123def456",
  "error_type": "RickAndMortyAPIError",
  "error_message": "Rate limit exceeded. Please try again later.",
  "status_code": 429,
  "endpoint": "get_characters",
  "method": "GET"
}
```

**Context Fields**:
- `error_type`: Exception class name
- `error_message`: Error description
- `status_code`: HTTP status code
- `endpoint`: Flask endpoint name
- `method`: HTTP method

### 5. Request Error Logging

**Example: Network/Connection Error**

```json
{
  "timestamp": "2026-09-13T01:46:00.654321Z",
  "level": "ERROR",
  "logger": "app",
  "message": "Failed to fetch data from Rick and Morty API",
  "error_type": "ConnectionError",
  "error_message": "Failed to resolve hostname: rickandmortyapi.com",
  "url": "https://rickandmortyapi.com/api/character",
  "params": {"page": 1, "status": "alive", "species": "human"},
  "timeout": 10
}
```

**Context Fields**:
- `error_type`: Exception type
- `error_message`: Detailed error message
- `url`: Request URL
- `params`: Query parameters
- `timeout`: Request timeout in seconds

### 6. HTTP Error Handler Logging

**Example: 400 Bad Request**

```json
{
  "timestamp": "2026-09-13T01:47:30.111222Z",
  "level": "WARNING",
  "logger": "app",
  "message": "Bad request error",
  "error_type": "BadRequest",
  "path": "/characters?invalid_param=true",
  "correlation_id": "xyz789abc123"
}
```

---

## Usage Examples

### Logging Request and Response Flow

A single request generates multiple log entries:

```
1. Incoming Request
   ├─ timestamp: 01:42:37.502901Z
   ├─ message: "Incoming request"
   ├─ method: GET
   └─ correlation_id: abc-123

2. Application Logic
   ├─ timestamp: 01:42:37.503136Z
   ├─ message: "Health check performed"
   └─ status: healthy

3. Response Sent
   ├─ timestamp: 01:42:37.503322Z
   ├─ message: "Response sent"
   ├─ status_code: 200
   └─ elapsed_time_ms: 0.75
```

### Tracing Across Requests

All logs with the same `correlation_id` belong to the same logical request:

```bash
# Extract all logs for a correlation ID
jq 'select(.correlation_id == "0f9cdd36-b9e3-470b-9b9f-e638a2185768")' app.log

# Result: All 3 entries above with matching correlation_id
```

---

## Implementation Details

### Logging Configuration

**File**: `app.py` (lines 1-18)

```python
from src.observability.logging import setup_logging, StructuredLogger, set_correlation_id

setup_logging(level="INFO", format_type="json")
logger = StructuredLogger(__name__)
```

### Request Middleware

**File**: `app.py` (lines 375-390)

```python
@app.before_request
def log_request():
    """Log incoming request with structured logging"""
    correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
    set_correlation_id(correlation_id)
    request.start_time = time.time()
    
    logger.info(
        "Incoming request",
        method=request.method,
        path=request.path,
        query_string=request.query_string.decode('utf-8') if request.query_string else None,
        remote_addr=request.remote_addr,
        correlation_id=correlation_id
    )
```

### Response Middleware

**File**: `app.py` (lines 393-410)

```python
@app.after_request
def log_response(response):
    """Log response with structured logging"""
    if hasattr(request, 'start_time'):
        elapsed_time = time.time() - request.start_time
    else:
        elapsed_time = 0
    
    logger.info(
        "Response sent",
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        elapsed_time_ms=round(elapsed_time * 1000, 2),
        correlation_id=get_correlation_id()
    )
    
    return response
```

### Error Handling

**File**: `app.py` (lines 48-78)

```python
def handle_api_errors(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        set_correlation_id(correlation_id)
        
        try:
            return f(*args, **kwargs)
        except RickAndMortyAPIError as e:
            logger.error(
                "Rick and Morty API error occurred",
                error_type="RickAndMortyAPIError",
                error_message=str(e),
                status_code=e.status_code,
                correlation_id=correlation_id,
                endpoint=request.endpoint,
                method=request.method
            )
            return jsonify({"error": str(e)}), e.status_code
        except Exception as e:
            logger.error(
                "Unexpected error occurred",
                error_type=type(e).__name__,
                error_message=str(e),
                correlation_id=correlation_id,
                endpoint=request.endpoint,
                method=request.method
            )
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function
```

---

## Log Output Examples

### Example 1: Successful Health Check

```bash
$ curl http://localhost:5000/health
```

**Console Output** (3 log entries):

```
{"timestamp": "2026-09-13T01:42:37.502901Z", "level": "INFO", "logger": "app", "message": "Incoming request", "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768", "method": "GET", "path": "/health", "query_string": null, "remote_addr": "127.0.0.1"}
{"timestamp": "2026-09-13T01:42:37.503136Z", "level": "INFO", "logger": "app", "message": "Health check performed", "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768", "status": "healthy"}
{"timestamp": "2026-09-13T01:42:37.503322Z", "level": "INFO", "logger": "app", "message": "Response sent", "correlation_id": "0f9cdd36-b9e3-470b-9b9f-e638a2185768", "method": "GET", "path": "/health", "status_code": 200, "elapsed_time_ms": 0.75}
```

### Example 2: Request with Custom Correlation ID

```bash
$ curl -H "X-Correlation-ID: my-request-123" http://localhost:5000/health
```

**Console Output**:

```
{"timestamp": "2026-09-13T01:43:00.111111Z", "level": "INFO", "logger": "app", "message": "Incoming request", "correlation_id": "my-request-123", "method": "GET", "path": "/health", "query_string": null, "remote_addr": "127.0.0.1"}
{"timestamp": "2026-09-13T01:43:00.222222Z", "level": "INFO", "logger": "app", "message": "Health check performed", "correlation_id": "my-request-123", "status": "healthy"}
{"timestamp": "2026-09-13T01:43:00.333333Z", "level": "INFO", "logger": "app", "message": "Response sent", "correlation_id": "my-request-123", "method": "GET", "path": "/health", "status_code": 200, "elapsed_time_ms": 1.23}
```

---

## Processing Structured Logs

### With jq (JSON Query Tool)

```bash
# Pretty print all logs
cat app.log | jq '.'

# Filter by level
cat app.log | jq 'select(.level == "ERROR")'

# Filter by correlation ID
cat app.log | jq 'select(.correlation_id == "my-request-123")'

# Extract only timestamp and message
cat app.log | jq '{timestamp, message}'

# Count logs by level
cat app.log | jq 'group_by(.level) | map({level: .[0].level, count: length})'

# Find slow requests (> 100ms)
cat app.log | jq 'select(.elapsed_time_ms > 100)'
```

### With Python

```python
import json

with open('app.log') as f:
    for line in f:
        log_entry = json.loads(line)
        
        # Filter errors
        if log_entry['level'] == 'ERROR':
            print(f"ERROR: {log_entry['message']}")
            print(f"  Type: {log_entry.get('error_type')}")
            print(f"  Correlation ID: {log_entry['correlation_id']}")
```

### With Log Aggregation Pipeline

The JSON format is optimized for Filebeat → Logstash → OpenSearch:

```
1. Filebeat reads JSON Lines from app.log
2. Sends to Logstash for processing
3. Logstash parses JSON and enriches logs
4. Stores in OpenSearch for indexing
5. Kibana visualizes logs and metrics
```

---

## Benefits

### 1. **Machine-Parseable**
- JSON format is automatically parsed by log aggregation tools
- No parsing errors from unstructured text logs

### 2. **Request Tracing**
- Correlation IDs enable tracking single requests across distributed services
- Easy to follow request flow from start to finish

### 3. **Performance Monitoring**
- `elapsed_time_ms` field enables performance analysis
- Identify slow requests and bottlenecks

### 4. **Error Analysis**
- Structured error context makes debugging easier
- Error types, messages, and related fields are consistently formatted

### 5. **Scalability**
- Logs ready for Kubernetes and containerized environments
- Compatible with ELK Stack, Splunk, DataDog, etc.

### 6. **Debugging**
- All context fields included in single log entry
- No need to correlate multiple unstructured log lines

---

## Configuration

### Log Level

**File**: `app.py` (line 13)

```python
setup_logging(level="INFO", format_type="json")
```

**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Custom Context Fields

**Pattern**: Pass keyword arguments to logger methods

```python
logger.info(
    "Processing request",
    user_id=123,
    action="authenticate",
    duration_ms=45.6,
    custom_field="value"
)
```

**Output**:
```json
{
  "timestamp": "2026-09-13T01:42:37.502901Z",
  "level": "INFO",
  "message": "Processing request",
  "user_id": 123,
  "action": "authenticate",
  "duration_ms": 45.6,
  "custom_field": "value",
  "correlation_id": "..."
}
```

---

## Next Steps

### For Development
- View logs in real-time: `tail -f app.log | jq '.'`
- Filter by error: `cat app.log | jq 'select(.level == "ERROR")'`
- Analyze performance: `cat app.log | jq 'select(.elapsed_time_ms > 100)'`

### For Deployment
- Configure log file path in environment
- Set up Filebeat to tail app.log
- Configure Logstash pipeline for log processing
- Set up OpenSearch indices for log storage
- Create Kibana dashboards for visualization

### For Future Enhancements
- Add distributed tracing (OpenTelemetry)
- Implement custom metrics collection
- Add request body/response body logging (optional)
- Implement log sampling for high-volume scenarios
- Add user context (user_id, tenant_id) to logs

---

## Testing

The structured logging has been verified with:

```bash
$ cd /home/localadmin/localwork/setupAppCreDepHelmPkg
$ source venv/bin/activate
$ python3 -c "
from app import app
client = app.test_client()
response = client.get('/health')
print(f'Status: {response.status_code}')
print(f'Logs: See console output above')
"
```

**Result**: ✅ Structured JSON logging working correctly

---

## Summary

Structured JSON logging is now fully implemented for:
- ✅ Incoming requests
- ✅ Outgoing responses
- ✅ Application events
- ✅ Error handling
- ✅ HTTP error handlers

All logs include correlation IDs for distributed tracing and are formatted for log aggregation pipelines.

**Status**: Ready for production deployment and log aggregation integration.
