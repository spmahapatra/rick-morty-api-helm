# PostgreSQL Health Check Error - Root Cause Analysis & Fix

## Error Message
```
rick-morty-postgres  | 2026-09-13 15:37:36.367 UTC [94] FATAL:  database "admin" does not exist
```

This error appeared repeatedly in PostgreSQL logs **every 10 seconds**.

---

## Root Cause Analysis

### The Problem
The Docker Compose health check was configured as:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin"]
  interval: 10s
```

### Why It Failed

**`pg_isready` Default Behavior:**

When `pg_isready` is invoked without a `-d` (database) flag, it **defaults to connecting to a database with the same name as the username**.

```bash
pg_isready -U admin
# ↓ Equivalent to ↓
pg_isready -U admin -d admin
```

Since our PostgreSQL setup does **not** have an "admin" database (only "rickmorty"), the health check failed:

```
FATAL: database "admin" does not exist
```

### Why Every 10 Seconds?

The health check interval was set to 10 seconds:
```yaml
interval: 10s
```

Docker runs the health check every 10 seconds. Each time it ran, PostgreSQL tried to connect to the non-existent "admin" database and logged a FATAL error.

---

## The Fix

### Before (Incorrect)
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### After (Correct)
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin -d rickmorty"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Key Change:** Added `-d rickmorty` to explicitly specify which database to check.

---

## Verification

### PostgreSQL Logs - Before Fix
```
2026-09-13 15:36:26.041 UTC [39] FATAL:  database "admin" does not exist
2026-09-13 15:36:36.081 UTC [48] FATAL:  database "admin" does not exist
2026-09-13 15:36:46.121 UTC [56] FATAL:  database "admin" does not exist
2026-09-13 15:36:56.192 UTC [64] FATAL:  database "admin" does not exist
2026-09-13 15:37:06.234 UTC [71] FATAL:  database "admin" does not exist
2026-09-13 15:37:16.273 UTC [79] FATAL:  database "admin" does not exist
2026-09-13 15:37:26.320 UTC [86] FATAL:  database "admin" does not exist
2026-09-13 15:37:36.367 UTC [94] FATAL:  database "admin" does not exist
(Pattern continues every 10 seconds...)
```

### PostgreSQL Logs - After Fix
```
PostgreSQL Database directory appears to contain a database; Skipping initialization

2026-09-13 15:40:19.266 UTC [1] LOG:  starting PostgreSQL 15.19
2026-09-13 15:40:19.283 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-09-13 15:40:19.303 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-09-13 15:40:19.325 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-09-13 15:40:19.349 UTC [1] LOG:  database system is ready to accept connections
(No FATAL errors - clean startup!)
```

### Container Status
```
NAME                  STATUS                      PORTS
rick-morty-api        Up 2 minutes (healthy)      0.0.0.0:5000->5000/tcp
rick-morty-postgres   Up 3 minutes (healthy)      0.0.0.0:5432->5432/tcp
rick-morty-redis      Up 3 minutes (healthy)      0.0.0.0:6379->6379/tcp
```

✅ All containers showing `(healthy)` status
✅ No more FATAL errors in logs
✅ Application functioning normally

---

## Database Configuration Reference

### Docker Compose Configuration
```yaml
postgres:
  image: postgres:15-alpine
  container_name: rick-morty-postgres
  environment:
    POSTGRES_USER: admin          # Username
    POSTGRES_PASSWORD: password   # Password
    POSTGRES_DB: rickmorty        # Initial database (this is what gets created!)
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U admin -d rickmorty"]
    interval: 10s
```

### Key Points
- **Username:** `admin`
- **Password:** `password`
- **Database:** `rickmorty` (the one that actually gets created)
- **Host:** `postgres` (service name in docker-compose)
- **Port:** `5432` (default PostgreSQL port)

### Application Connection String
```
postgresql://admin:password@postgres:5432/rickmorty
                             ↑ service name from docker-compose
                                          ↑ actual database name
```

---

## Lessons Learned

1. **Health check commands should be explicit** - Don't rely on defaults
2. **Read tool documentation carefully** - `pg_isready -U admin` is ambiguous
3. **Match database name in health checks** - Use the actual database being created
4. **Monitor logs for health check patterns** - Recurring FATAL errors at regular intervals often indicate a health check problem

---

## Summary

The "FATAL: database admin does not exist" error was caused by a PostgreSQL health check trying to connect to a database that didn't exist. 

**Fix:** Explicitly specify the correct database name in the health check command.

**Result:** Clean PostgreSQL logs, all containers healthy, application working normally.
