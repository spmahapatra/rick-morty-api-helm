# Logging Output Locations - What Gets Logged Where?

**Date**: 2026-09-13  
**Status**: ✅ CLARIFICATION

---

## Current Logging Configuration

**File**: `app.py` (line 13)

```python
setup_logging(level="INFO", format_type="json")
```

This configuration has:
- ✅ **Console Output** (STDOUT)
- ❌ **No file output** (log_file parameter not specified)

---

## What GETS Logged

### Where It Goes
- **Console/Terminal**: Yes ✅
- **Docker logs**: Yes ✅ (if containerized)
- **File on disk**: No ❌ (currently)
- **Log aggregation service**: No ❌ (not yet configured)

### What Is Logged to Console

All structured JSON logs are printed to **STDOUT**:

```
{"timestamp": "2026-09-13T01:48:52.936899Z", "level": "INFO", ...}
{"timestamp": "2026-09-13T01:48:52.937058Z", "level": "INFO", ...}
{"timestamp": "2026-09-13T01:48:52.937180Z", "level": "INFO", ...}
```

**Examples of what gets logged**:
- ✅ Incoming HTTP requests
- ✅ Outgoing HTTP responses
- ✅ Application events (health checks)
- ✅ Error messages
- ✅ Performance metrics (elapsed time)
- ✅ Correlation IDs
- ✅ Request context (method, path, query params)

### Specific Log Entries

**Request Logging** ✅
```json
{
  "message": "Incoming request",
  "method": "GET",
  "path": "/health",
  "query_string": null,
  "remote_addr": "127.0.0.1"
}
```

**Response Logging** ✅
```json
{
  "message": "Response sent",
  "status_code": 200,
  "elapsed_time_ms": 0.46
}
```

**Error Logging** ✅
```json
{
  "level": "ERROR",
  "message": "Rick and Morty API error occurred",
  "error_type": "RickAndMortyAPIError",
  "error_message": "Rate limit exceeded"
}
```

**Health Check** ✅
```json
{
  "message": "Health check performed",
  "status": "healthy"
}
```

---

## What DOESN'T Get Logged (Currently)

### Response Body/Payload

**NOT logged**:
```json
❌ {"data": [...characters...], "pagination": {...}}
```

**Why**: Could contain sensitive data; usually not needed for debugging

**Can enable if needed**: Add custom logging to endpoint handlers

---

### Request Body/Payload

**NOT logged**:
```json
❌ POST body content
❌ Request headers (except correlation ID)
```

**Why**: GET requests don't have body; could expose sensitive data

**Can enable if needed**: Add custom logging with privacy controls

---

### Database Queries

**NOT logged**:
```json
❌ SELECT * FROM characters WHERE...
❌ Query execution time
❌ Row counts
```

**Why**: Database layer not yet implemented (Phase 2)

**Will be added**: In Phase 2 when persistence layer is implemented

---

### Cache Operations

**NOT logged**:
```json
❌ Cache hit/miss
❌ Cache key accessed
❌ Cache eviction
```

**Why**: Cache layer not yet implemented (Phase 3)

**Will be added**: In Phase 3 when caching layer is implemented

---

### Custom Application Events

**NOT logged** (by default):
```json
❌ Custom business logic events
❌ User actions
❌ Data transformations
```

**Can be added**: Using `logger.info()` with custom fields

**Example**:
```python
from app import logger

# Custom logging in your code
logger.info(
    "Character processed",
    character_id=123,
    species="human",
    status="alive"
)
```

---

## How to Enable File Logging

### Option 1: Simple File Output (Recommended)

**Current Code** (app.py, line 13):
```python
setup_logging(level="INFO", format_type="json")
```

**Modified Code** (with file output):
```python
setup_logging(
    level="INFO", 
    format_type="json",
    log_file="/tmp/app.log"  # ← Add this line
)
```

**Result**:
- ✅ Logs go to STDOUT (console/terminal)
- ✅ Logs also saved to `/tmp/app.log`
- ✅ Both destinations receive identical JSON logs

### Option 2: File-Only Logging

```python
import logging

# Only write to file, not console
root_logger = logging.getLogger()
file_handler = logging.FileHandler("/tmp/app.log")
file_handler.setFormatter(JsonFormatter())
root_logger.addHandler(file_handler)
```

---

## Docker/Container Logging

If running in Docker, logs go to **container STDOUT**, which Docker captures.

### View Docker Logs

```bash
# If running in Docker Compose
docker-compose logs -f app

# If running in Kubernetes
kubectl logs -f deployment/rick-morty-api

# If running standalone Docker
docker logs -f <container_id>
```

**Note**: No file needed! Docker captures all STDOUT automatically.

---

## Log Viewing Scenarios

### Scenario 1: Run App in Terminal

```bash
$ python app.py
```

**Output** (see in terminal directly):
```
{"timestamp": "2026-09-13T01:48:52.936899Z", "level": "INFO", ...}
{"timestamp": "2026-09-13T01:48:52.937058Z", "level": "INFO", ...}
```

**Where logs go**: Terminal screen only ✅

---

### Scenario 2: Run App in Docker

```bash
$ docker run rick-morty-api
```

**View logs**:
```bash
$ docker logs <container_id> | jq '.'
```

**Where logs go**: Docker container STDOUT → Docker daemon ✅

---

### Scenario 3: Run App in Kubernetes

**Pod logs**:
```bash
$ kubectl logs -f pod/rick-morty-api-xyz123
```

**Where logs go**: Kubernetes pod STDOUT → Kubelet ✅

---

### Scenario 4: Run App with File Output

```python
setup_logging(level="INFO", format_type="json", log_file="/var/log/app.log")
```

**View logs**:
```bash
$ tail -f /var/log/app.log | jq '.'
```

**Where logs go**: STDOUT + `/var/log/app.log` ✅✅

---

## Log Aggregation Pipeline (Future)

### Current State: Local Logs Only

```
Application
    ↓
    ├→ STDOUT (console)
    └→ File (if enabled)
```

### Future State: With Log Aggregation

```
Application
    ↓
    ├→ STDOUT
    └→ File (/var/log/app.log)
         ↓
    Filebeat (reads file)
         ↓
    Logstash (processes JSON)
         ↓
    OpenSearch (stores/indexes)
         ↓
    Kibana (visualizes)
```

---

## Recommendation: What to Do Now

### For Development

**Current setup is good** ✅

```python
setup_logging(level="INFO", format_type="json")
```

- Logs appear in terminal
- Easy to see in real-time
- Can pipe to `jq` for filtering
- No disk usage

### For Production

**Add file output** ✅

```python
setup_logging(
    level="INFO",
    format_type="json", 
    log_file="/var/log/rick-morty-api/app.log"
)
```

- Logs go to both console and file
- Docker/Kubernetes captures console
- Filebeat monitors the file
- Integrates with log aggregation

### For Kubernetes Deployments

**Use console logging only** ✅

```python
setup_logging(level="INFO", format_type="json")
```

- Kubernetes automatically captures container STDOUT
- Don't need files on ephemeral pods
- Kubelet sends to centralized logging
- Works with ELK Stack natively

---

## How to Enable File Logging (Step by Step)

### Step 1: Modify app.py

**Find line 13**:
```python
setup_logging(level="INFO", format_type="json")
```

**Change to**:
```python
setup_logging(level="INFO", format_type="json", log_file="/tmp/app.log")
```

### Step 2: Restart Application

```bash
# Kill current process
Ctrl+C

# Restart
python app.py
```

### Step 3: Verify File Output

**Terminal 1**: Keep app running
```bash
$ python app.py
```

**Terminal 2**: Monitor file
```bash
$ tail -f /tmp/app.log | jq '.'
```

**Terminal 3**: Make requests
```bash
$ curl http://localhost:5000/health
```

**Terminal 2 Output**:
```json
{"timestamp": "2026-09-13T01:48:52.936899Z", "level": "INFO", ...}
{"timestamp": "2026-09-13T01:48:52.937058Z", "level": "INFO", ...}
{"timestamp": "2026-09-13T01:48:52.937180Z", "level": "INFO", ...}
```

---

## Summary Table

| Aspect | Currently | With File Logging | With Docker | With Kubernetes |
|--------|-----------|-------------------|-------------|-----------------|
| Console Output | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| File on Disk | ❌ No | ✅ Yes | ❌ No* | ❌ No* |
| Docker Logs | N/A | ✅ Yes | ✅ Yes | ✅ Yes |
| K8s Logs | N/A | N/A | N/A | ✅ Yes |
| Log Aggregation | ❌ No | ⚠️ Ready | ⚠️ Ready | ⚠️ Ready |

*Can add if needed

---

## What's NOT Logged vs What IS Logged

### ✅ IS Logged

- HTTP request (method, path, query string, client IP)
- HTTP response (status code, elapsed time)
- Application events (health checks)
- Errors (type, message, status code)
- Correlation IDs (for tracing)
- Log timestamp and level
- Performance metrics (timing)

### ❌ NOT Logged (Currently)

- Request/response body content
- HTTP headers (except correlation ID extraction)
- Database queries
- Cache operations
- Custom business events (unless explicitly coded)
- Request body parameters
- Response JSON payload

### ⚠️ Can Be Added

- Response body logging (for debugging)
- Request headers logging (selectively)
- Database query logging (Phase 2)
- Cache hit/miss logging (Phase 3)
- Custom business events (anywhere in code)

---

## Next Steps

### Immediate

- ✅ Structured JSON logging is working
- ✅ Logs appear in console
- Can pipe to `jq` for analysis

### Optional (Development)

- Enable file output for persistence
- Create log rotation (for file growth)
- Set up log aggregation

### For Production

- Enable file output to `/var/log/rick-morty-api/app.log`
- Configure log rotation (logrotate)
- Set up Filebeat to monitor log file
- Configure Logstash pipeline
- Deploy OpenSearch for storage
- Create Kibana dashboards

---

## Code Example: Testing Current Logging

```bash
$ cd /home/localadmin/localwork/setupAppCreDepHelmPkg
$ source venv/bin/activate
$ python3 << 'EOF'
from app import app

client = app.test_client()

# This will print logs to console
response = client.get('/health')
print(f"\n✅ Response: {response.status_code}")
print("👆 See JSON logs above ☝️")
EOF
```

**Output** (you'll see):
```
{"timestamp": "...", "message": "Incoming request", ...}
{"timestamp": "...", "message": "Health check performed", ...}
{"timestamp": "...", "message": "Response sent", ...}

✅ Response: 200
👆 See JSON logs above ☝️
```

---

## Conclusion

**Currently**:
- ✅ All logs output to console/terminal in JSON format
- ✅ Logs are structured and machine-parseable
- ✅ Correlation IDs enable request tracing
- ✅ Can pipe to `jq` for filtering and analysis
- ❌ No file persistence (optional)
- ❌ No log aggregation (future phase)

**To add file output**: Change one line in app.py and restart

**To add log aggregation**: Deploy Filebeat/Logstash/OpenSearch (future)

---

**Status**: Ready for review and file logging enablement ✅
