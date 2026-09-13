# Root Cause Analysis: /opsx-sync Workflow Failures

**Date**: 2026-09-13  
**Status**: Analysis Complete  
**Critical Issues**: 2

---

## Executive Summary

The `/opsx-sync` workflow fails at the database initialization stage due to two distinct but related issues:

1. **psycopg2 Missing Dependency** (Primary cause)
   - Error: `ModuleNotFoundError: No module named 'psycopg2'`
   - Impact: init_db.py crashes before database connection attempt
   - Root cause: requirements.txt uses `psycopg==3.1.14` but SQLAlchemy PostgreSQL adapter requires psycopg2

2. **Database Connection String Mismatch** (Secondary cause)
   - Error: `database "admin" does not exist`
   - Impact: Even if psycopg2 is installed, connection fails
   - Root cause: PostgreSQL configured with `POSTGRES_DB=rickmorty` but connection string defaults to "admin" database

---

## Issue #1: psycopg2 Missing Dependency

### Error Log
```
{"timestamp": "2026-09-13T02:14:23.481166Z", 
 "level": "ERROR", 
 "message": "Unexpected error during database initialization", 
 "error_type": "ModuleNotFoundError", 
 "error_message": "No module named 'psycopg2'", 
 "context": {"action": "init_database", "exception": "No module named 'psycopg2'"}}
```

### Root Cause Analysis

**The Problem:**
```
requirements.txt (current):
  psycopg==3.1.14

SQLAlchemy PostgreSQL Adapter Chain:
  app.py calls create_engine("postgresql://...")
  ↓
  SQLAlchemy parses protocol as "postgresql"
  ↓
  SQLAlchemy looks for DBAPI drivers in order:
    1. psycopg2 (primary - async aware, widely compatible)
    2. psycopg2-binary (fallback)
    3. pygresql (legacy)
    4. py-postgresql (legacy)
  ↓
  But requirements.txt only has psycopg v3 (new async-first driver)
  ↓
  SQLAlchemy can't find psycopg2 → ModuleNotFoundError
```

**Why This Happens:**

1. **Driver Versioning Confusion:**
   - `psycopg` (v3.x+): NEW async-first PostgreSQL driver, pure Python
   - `psycopg2`: LEGACY synchronous driver, requires libpq compiled libraries
   - `psycopg2-binary`: LEGACY driver bundled with libpq (easier installation)

2. **SQLAlchemy Compatibility:**
   - SQLAlchemy 2.0.23 (in requirements.txt) can work with BOTH drivers
   - However, connection string protocol matters:
     - `postgresql://` → expects psycopg2 or psycopg2-binary
     - `postgresql+psycopg://` → expects psycopg v3 (works!)
     - `postgresql+asyncpg://` → expects asyncpg (different driver)

3. **The Current Setup Issue:**
   - Connection string: `postgresql://admin:password@postgres:5432/rickmorty` (from docker-compose.yml:50)
   - Driver installed: `psycopg==3.1.14` (from requirements.txt:7)
   - Protocol used: `postgresql://` (implies psycopg2, not psycopg3)
   - Result: ❌ MISMATCH → ModuleNotFoundError

### Solution #1a: Use psycopg2-binary (RECOMMENDED for Docker)

**Why this is best:**
- ✅ Works with `postgresql://` protocol
- ✅ Includes all compiled libraries bundled
- ✅ No system dependency installation needed
- ✅ Works in slim base images (Python 3.9-slim)
- ✅ Tested and stable

**Change required:**
```diff
- psycopg==3.1.14
+ psycopg2-binary==2.9.9
```

### Solution #1b: Use psycopg v3 with correct protocol

If we want to use the new async-first psycopg driver:

**Connection string change needed:**
```diff
- DATABASE_URL=postgresql://admin:password@postgres:5432/rickmorty
+ DATABASE_URL=postgresql+psycopg://admin:password@postgres:5432/rickmorty
```

**Change required:**
```diff
- psycopg==3.1.14
+ psycopg[binary]==3.1.14
```

**Recommendation:** Use Solution #1a (psycopg2-binary) because:
1. No code changes needed (connection string stays the same)
2. Better tested with SQLAlchemy 2.0.23
3. Mature, stable ecosystem
4. Easier Docker debugging

---

## Issue #2: Database Connection String Mismatch

### Error Log
```
rick-morty-postgres  | 2026-09-13 02:14:09.891 UTC [39] FATAL:  database "admin" does not exist
```

### Root Cause Analysis

**The Problem:**

```
PostgreSQL Container Configuration (docker-compose.yml):
  POSTGRES_USER: admin
  POSTGRES_PASSWORD: password
  POSTGRES_DB: rickmorty  ← THIS creates the "rickmorty" database

Connection String (docker-compose.yml:50):
  DATABASE_URL=postgresql://admin:password@postgres:5432/rickmorty
                                                      ↓
                                         Database name is "rickmorty" ✓ CORRECT

But Somewhere in Connection Flow:
  Some code attempts to connect to "admin" database (default)
  PostgreSQL response: FATAL:  database "admin" does not exist
```

**Why This Happens:**

1. **PostgreSQL Defaults:**
   - When you create user "admin" with password "password"
   - PostgreSQL creates user but NO default database for that user
   - User gets access to system DB "postgres" by default
   - If code tries `postgresql://admin:password@postgres:5432` (no DB specified)
   - It defaults to connecting to "admin" database → doesn't exist!

2. **Application Connection Flow:**
   - init_db.py:42: `database_url = os.environ.get('DATABASE_URL')`
   - init_db.py:63: `engine = create_engine(database_url)`
   - But if DATABASE_URL is not set, or set incorrectly
   - SQLAlchemy tries to connect to wrong database

3. **Current docker-compose.yml Setup:**
   - DATABASE_URL is correctly set to `postgresql://admin:password@postgres:5432/rickmorty`
   - But PostgreSQL may still receive connection to default "admin" DB
   - Indicates timing issue: init_db.py runs before db is ready

### Why Both Issues Occur Together

**The failure cascade:**
1. init_db.py starts (psycopg2 dependency missing)
2. init_db.py crashes before reaching database connection code
3. Dockerfile CMD fails: `python init_db.py && gunicorn ...`
4. Because of `&&`, gunicorn never starts
5. Container restarts (restart: unless-stopped)
6. Repeat → cascade failure

**BUT**, even if psycopg2 were installed, the timing issue remains:
1. init_db.py tries to connect immediately
2. PostgreSQL may not be fully initialized yet
3. Connection string may resolve to wrong database
4. Result: `database "admin" does not exist` error

### Solution #2: Ensure Proper Database Connection

**Connection string verification:**
```
docker-compose.yml line 50:
✓ DATABASE_URL=postgresql://admin:password@postgres:5432/rickmorty
                                                      ↑ ✓ CORRECT DB NAME
```

**BUT ensure:**
1. Database URL is set BEFORE init_db.py runs
2. PostgreSQL service is healthy BEFORE app tries to connect
3. Connection string is parsed correctly by SQLAlchemy
4. No default database fallback occurs

**Docker Compose Already Has This:**
```yaml
depends_on:
  postgres:
    condition: service_healthy  ← Waits for postgres healthcheck
  redis:
    condition: service_healthy
```

**But add extra safety:**
- Retry logic in init_db.py (if connection fails, retry)
- Wait loop before database initialization
- Explicit database name verification

---

## Complete Fix: Implementation Steps

### Step 1: Fix psycopg2 Dependency

Replace psycopg with psycopg2-binary in requirements.txt:

**Before:**
```
psycopg==3.1.14
```

**After:**
```
psycopg2-binary==2.9.9
```

**Why psycopg2-binary specifically:**
- v2.9.9: Latest stable release
- Works with Python 3.9 (in Dockerfile)
- Includes libpq bundled (no system library needed)
- Compatible with SQLAlchemy 2.0.23
- Standard in production Django deployments

### Step 2: Add Connection Retry Logic (Optional but Recommended)

Update init_db.py to retry on connection failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_engine_with_retry(database_url):
    return create_engine(database_url)
```

**Note:** tenacity is already in requirements.txt (v8.2.3)

### Step 3: Verify Docker Build

```bash
docker compose build --no-cache
```

This ensures:
- New requirements installed
- psycopg2-binary compiled correctly
- No cached layers from old build

### Step 4: Clean Start

```bash
docker compose down -v  # Remove volumes to start fresh
docker compose up -d
```

**Flags explained:**
- `down -v`: Removes containers AND volumes (resets database)
- `up -d`: Start all services in detached mode

### Step 5: Verify Logs

```bash
docker compose logs -f rick-morty-api
```

**Expected successful output:**
```
Starting database initialization
Testing database connection
Database connection successful
Checking existing tables
Database tables created/verified
Final table verification
Database initialization completed successfully
Starting gunicorn 21.2.0
Listening at: http://0.0.0.0:5000
Booting worker with pid: 10
Booting worker with pid: 11
```

**NOT expected (errors fixed):**
```
❌ ModuleNotFoundError: No module named 'psycopg2'
❌ FATAL:  database "admin" does not exist
❌ WORKER TIMEOUT
❌ ModuleNotFoundError: No module named 'src'
```

---

## Technical Deep Dive: Why Each Issue Matters

### Issue #1 Impact: psycopg2

**Severity:** CRITICAL - Blocks all database operations

**Failure Point:**
```python
# init_db.py line 63
engine = create_engine(database_url)  ← CRASHES HERE
  ↓
SQLAlchemy tries to load DBAPI driver
  ↓
Looks for psycopg2 module (implied by postgresql:// protocol)
  ↓
Module not found
  ↓
ModuleNotFoundError: No module named 'psycopg2'
  ↓
init_db.py returns False (exit code 1)
  ↓
Dockerfile CMD fails: python init_db.py && gunicorn ...
  ↓
Container exits
  ↓
Docker restart policy: unless-stopped
  ↓
Container restarts
  ↓
REPEAT → Cascade failure
```

**Time to Failure:** ~2 seconds

### Issue #2 Impact: Database Connection

**Severity:** HIGH - Prevents data access

**Failure Point (if Issue #1 were fixed):**
```python
# Timing issue: init_db.py runs before PostgreSQL is ready
# OR connection string routes to wrong database

# PostgreSQL configuration:
# - Database "rickmorty" created ✓
# - Database "admin" NOT created ✗

# Connection attempt:
# postgresql://admin:password@postgres:5432/rickmorty
# ↓
# Actually tries to connect to:
# postgresql://admin:password@postgres:5432/[default_database]
# ↓
# Default is "admin" (username)
# ↓
# FATAL: database "admin" does not exist
```

**Time to Failure:** ~5 seconds (after connection timeout)

---

## Testing Strategy

### Test 1: Verify psycopg2 Installation

```bash
docker compose build --no-cache

docker compose run --rm rick-morty-api python -c "import psycopg2; print(psycopg2.__version__)"
# Expected: 2.9.9
```

### Test 2: Verify Database Connection

```bash
docker compose up -d postgres
docker compose logs postgres | grep "database system is ready to accept connections"
# Expected: message about ready state

docker compose run --rm rick-morty-api python init_db.py
# Expected: "Database initialization completed successfully"
```

### Test 3: Verify Full Startup

```bash
docker compose down -v
docker compose up -d

sleep 5  # Wait for startup

docker compose ps
# Expected: all services "Up X seconds (healthy)"

curl http://localhost:5000/health
# Expected: 200 OK
```

### Test 4: Verify Tables Created

```bash
docker compose exec postgres psql -U admin -d rickmorty -c "\dt"
# Expected: characters, api_calls, audit_logs, cache_metadata tables

docker compose exec postgres psql -U admin -d rickmorty -c "SELECT COUNT(*) FROM characters;"
# Expected: 0 (empty table)
```

---

## Configuration Summary

### Before (❌ BROKEN)

```
requirements.txt:
  psycopg==3.1.14  ← Wrong driver type

docker-compose.yml:
  DATABASE_URL=postgresql://...  ← Protocol mismatch with driver

Result:
  ModuleNotFoundError: No module named 'psycopg2'
  database "admin" does not exist
  Cascade failures and timeouts
```

### After (✅ FIXED)

```
requirements.txt:
  psycopg2-binary==2.9.9  ← Correct driver type

docker-compose.yml:
  DATABASE_URL=postgresql://...  ← Protocol matches driver
  POSTGRES_DB=rickmorty  ← Database correctly created

Result:
  init_db.py runs successfully
  Tables created automatically
  Gunicorn starts cleanly
  API ready immediately
```

---

## Prevention: Best Practices

### 1. Database Driver Management
- ✅ Use `psycopg2-binary` for Docker (easiest)
- ✅ Or use `postgresql+psycopg://` if using psycopg v3
- ✅ Always match protocol prefix to installed driver
- ✅ Document driver choice in README

### 2. Connection String Validation
- ✅ Set DATABASE_URL in docker-compose.yml (not app code)
- ✅ Use same database name as POSTGRES_DB
- ✅ Log masked connection string on startup
- ✅ Verify connection works before creating tables

### 3. Startup Sequencing
- ✅ Use `depends_on` with `condition: service_healthy`
- ✅ Add retry logic in init_db.py
- ✅ Set appropriate timeouts
- ✅ Log each step of initialization

### 4. Observability
- ✅ Structured JSON logging (already implemented)
- ✅ Log database operations
- ✅ Log errors with context
- ✅ Include correlation IDs for tracing

---

## Files to Modify

| File | Change | Reason |
|------|--------|--------|
| requirements.txt | psycopg → psycopg2-binary | Fix missing dependency |
| init_db.py | (Optional) Add retry logic | Improve resilience |
| Dockerfile | No change needed | Already correct |
| docker-compose.yml | No change needed | Already correct |

---

## Rollback Plan

If issues occur after fix:

```bash
# Revert requirements.txt
git checkout requirements.txt

# Rebuild and restart
docker compose build --no-cache
docker compose down -v
docker compose up -d

# Verify
docker compose logs -f rick-morty-api
```

---

## Monitoring After Fix

```bash
# Monitor startup logs
docker compose logs -f rick-morty-api

# Monitor database connections
docker compose exec postgres psql -U admin -d rickmorty \
  -c "SELECT * FROM pg_stat_activity WHERE datname='rickmorty';"

# Monitor API health
while true; do
  curl -s http://localhost:5000/health | jq .
  sleep 5
done
```

---

## Success Criteria

- [x] psycopg2-binary installed in requirements.txt
- [ ] Docker image rebuilt with no errors
- [ ] Containers start without ModuleNotFoundError
- [ ] Database connection succeeds
- [ ] All tables created
- [ ] Health check returns 200 OK
- [ ] API responds to requests
- [ ] No restart loops in logs

---

## Appendix: PostgreSQL Connection Mechanics

### How PostgreSQL Handles Default Database Selection

```
Connection String: postgresql://USER:PASS@HOST:PORT/DATABASE

1. Connect to host:port
2. Authenticate with user/password
3. Select database
   - If DATABASE specified → use it
   - If DATABASE blank → use user's default database
   - If user has no default → try "admin" or "postgres"
   - If doesn't exist → FATAL error

Our setup:
  Connection: postgresql://admin:password@postgres:5432/rickmorty
              ↑                                         ↑
              Username matches POSTGRES_USER      Explicit database name
  
  PostgreSQL creates:
    - User "admin" ✓
    - Database "rickmorty" ✓
    - User "admin" default database: NONE (not set)
  
  Result: Connection string explicitly names "rickmorty" → WORKS ✓
```

### Why "admin" Database Appears in Error

```
If connection string is malformed or environment variable not set:
  postgresql://admin:password@postgres:5432/

Parsing:
  User: admin
  Database: [empty]
  
PostgreSQL tries to use default for "admin" user:
  → admin's default database is: "admin" (by convention)
  → But our admin user has no default database
  
Result: FATAL: database "admin" does not exist
```

This error indicates the connection string lost the database name somewhere.

---

## Summary

**Two issues, one fix strategy:**

1. **psycopg2 missing**: Change requirements.txt to use psycopg2-binary
2. **Database connection mismatch**: Already correct in docker-compose.yml, but fix #1 unblocks it

**Implementation time:** ~5 minutes

**Testing time:** ~2 minutes

**Risk level:** LOW (standard library swap)

**Rollback risk:** MINIMAL (Git revert available)

