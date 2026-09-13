# Data Persistence Specification

## Feature: PostgreSQL Database Schema & Persistence

### Functional Requirements

#### REQ-2.1: Database Schema Design
Implement normalized schema for storing characters, query results, and audit trails.

**Tables:**

1. **characters** - Denormalized cache of character data
   - `id` (INTEGER, PRIMARY KEY) - Character ID from Rick and Morty API
   - `name` (VARCHAR(255), NOT NULL)
   - `status` (VARCHAR(20)) - alive, dead, unknown
   - `species` (VARCHAR(100))
   - `type` (VARCHAR(255))
   - `gender` (VARCHAR(20))
   - `origin_name` (VARCHAR(255))
   - `origin_url` (VARCHAR(500))
   - `location_name` (VARCHAR(255))
   - `location_url` (VARCHAR(500))
   - `image_url` (VARCHAR(500))
   - `url` (VARCHAR(500)) - Source API URL
   - `created_at` (TIMESTAMP, DEFAULT: NOW()) - When inserted
   - `updated_at` (TIMESTAMP, DEFAULT: NOW()) - Last update
   - `synced_at` (TIMESTAMP) - Last sync from upstream API
   - INDEX: `(status, species, origin_name)` for filter queries
   - INDEX: `(updated_at)` for incremental sync detection

2. **query_results** - Cached aggregated queries for analytics
   - `id` (BIGSERIAL, PRIMARY KEY)
   - `query_params` (JSONB) - page, limit, sort_by, sort_order
   - `result_count` (INTEGER)
   - `result_data` (JSONB) - Character list snapshot
   - `created_at` (TIMESTAMP, DEFAULT: NOW())
   - `expires_at` (TIMESTAMP) - When to purge
   - INDEX: `(query_params JSONB)` for JSONB searches
   - INDEX: `(created_at)` for retention policies

3. **api_calls** - Audit trail of all upstream API interactions
   - `id` (BIGSERIAL, PRIMARY KEY)
   - `endpoint` (VARCHAR(255)) - /characters, /character/:id
   - `request_params` (JSONB)
   - `response_status_code` (SMALLINT)
   - `response_time_ms` (INTEGER)
   - `cache_hit` (BOOLEAN)
   - `retry_count` (SMALLINT)
   - `error_message` (TEXT)
   - `correlation_id` (UUID) - Trace across systems
   - `created_at` (TIMESTAMP, DEFAULT: NOW())
   - INDEX: `(correlation_id)` for request tracing
   - INDEX: `(created_at)` for time-range queries
   - RETENTION: Auto-delete after 90 days

4. **metrics** - Pre-aggregated performance metrics
   - `id` (BIGSERIAL, PRIMARY KEY)
   - `endpoint` (VARCHAR(255))
   - `timestamp` (TIMESTAMP) - 1-minute bucket
   - `request_count` (INTEGER)
   - `error_count` (INTEGER)
   - `cache_hits` (INTEGER)
   - `cache_misses` (INTEGER)
   - `latency_p50_ms` (REAL)
   - `latency_p95_ms` (REAL)
   - `latency_p99_ms` (REAL)
   - INDEX: `(endpoint, timestamp DESC)` for time-series queries
   - RETENTION: Keep 30 days (90 days if archive enabled)

**Acceptance Criteria:**
- Schema supports all functional requirements
- Indexes optimize the 5 most common queries
- Foreign key constraints enforce referential integrity
- Retention policies automatically purge old data

#### REQ-2.2: Data Synchronization Strategy
- Sync character data during cache misses
- Implement incremental sync: Only update records modified since last sync
- Upsert logic: INSERT if new, UPDATE if exists
- Handle race conditions with UNIQUE constraints and ON CONFLICT clauses

**Acceptance Criteria:**
- No duplicate character records
- Sync operations are idempotent
- Incremental sync reduces database load by 80% vs. full sync

#### REQ-2.3: Database Migrations
- Use Alembic (Python SQL migration tool) for version control
- Auto-migrate on application startup
- Rollback capability for failed migrations
- Migration validation: Verify schema after each migration

**Acceptance Criteria:**
- Migrations are reversible
- Application won't start if database schema is incompatible
- Migration history is tracked in `alembic_version` table

#### REQ-2.4: Data Persistence API
- Expose `/data-sync` endpoint to trigger manual sync
- Expose `/analytics/top-characters` to query character popularity
- Expose `/analytics/query-patterns` for query usage analysis
- Expose `/data-retention` admin endpoint to manage data lifecycle

**Acceptance Criteria:**
- All data queries are read-only and don't block writes
- Analytics queries complete within 2 seconds

#### REQ-2.5: Connection Pool Management
- Implement connection pooling with configurable size
- Min pool size: 5, Max pool size: 20
- Idle connection timeout: 30 minutes
- Stale connection detection and recycling
- Connection exhaustion alerts

**Acceptance Criteria:**
- Database connections never exceed max pool size
- Idle connections are recycled
- Connection pool status is visible in health check

### Performance Requirements

- Connection pool: Max 20 concurrent connections
- Query timeout: 30 seconds (long queries fail safely)
- Data sync latency: < 2 seconds for 50 character batch
- Analytics query latency: < 5 seconds (p99)
- Storage: Compact index usage with INCLUDE columns where possible

### Configuration Requirements

```env
DATABASE_URL=postgresql://user:password@localhost:5432/rickmorty
DATABASE_POOL_SIZE=10
DATABASE_POOL_TIMEOUT=30
DATABASE_QUERY_TIMEOUT=30
DATABASE_AUTO_MIGRATE=true
DATABASE_RETENTION_DAYS=90
DATABASE_ARCHIVE_ENABLED=false
```

---

## Feature: Data Synchronization Scenarios

### Scenario 1: New Character Sync on Cache Miss
**Given** a client requests `/characters/99` (a new character)
**And** the character is not in cache or database
**When** the upstream API returns character data
**Then** the character is inserted into the `characters` table
**And** an `api_calls` record is created with `cache_hit: false`
**And** `synced_at` is set to current timestamp
**And** response latency is logged

### Scenario 2: Incremental Sync Detects Updates
**Given** character "Rick Sanchez" was last synced 1 hour ago
**And** the upstream API has a newer `updated_at` timestamp
**When** the background sync job runs
**Then** only the character record with `updated_at > last_sync_time` is fetched
**And** the local record is updated via UPSERT
**And** sync operation log shows: "sync_type": "incremental", "records_updated": 1

### Scenario 3: Race Condition: Concurrent Writes
**Given** two concurrent requests both miss the cache for the same character
**When** both threads attempt to INSERT the character
**Then** PostgreSQL UNIQUE constraint triggers CONFLICT
**And** the second write executes ON CONFLICT DO UPDATE
**And** both threads receive the same final record state
**And** log shows: "upsert_conflict_handled": true

### Scenario 4: Retention Policy Auto-Purges Old Data
**Given** an `api_calls` record was created 91 days ago
**And** `DATABASE_RETENTION_DAYS=90`
**When** the nightly retention job runs
**Then** records older than 90 days are deleted
**And** log shows: "retention_job_deleted": 1234, "older_than_days": 90

### Scenario 5: Database Connection Pool Exhaustion
**Given** all 20 connection pool slots are in use
**When** a new request arrives requiring a database connection
**Then** the request waits in queue for up to 30 seconds
**And** if a connection becomes available, request proceeds
**And** if timeout expires, request fails with 503 Service Unavailable
**And** health check reports: "db_connection_pool": "exhausted"

---

## Feature: Analytics & Reporting

### Scenario 6: Query Pattern Analysis
**Given** clients have made 1000 requests over 1 hour
**When** `/analytics/query-patterns` endpoint is called
**Then** top 10 most common queries are returned
**And** includes: `query`, `count`, `cache_hit_rate`, `avg_latency_ms`
**Example Response:**
```json
{
  "patterns": [
    {
      "query": "?page=1&limit=10&sort_by=name&sort_order=asc",
      "count": 342,
      "cache_hit_rate": 0.98,
      "avg_latency_ms": 12
    }
  ]
}
```

### Scenario 7: Character Popularity Metrics
**Given** 5000 character detail requests over 30 days
**When** `/analytics/top-characters` endpoint is called
**Then** top 20 most queried characters are returned
**And** includes: `character_id`, `name`, `request_count`, `cache_hit_rate`
**And** data supports identifying most popular characters for caching priority

---

## Non-Functional Requirements

| Requirement | Target | Priority |
|---|---|---|
| Database availability | 99.9% | P0 |
| Connection pool efficiency | < 5% idle waste | P1 |
| Query response time (analytics) | < 5s p99 | P1 |
| Data sync latency | < 2s for 50 records | P1 |
| Retention policy accuracy | 100% (no data loss before TTL) | P0 |
| Upsert race condition handling | 100% guaranteed integrity | P0 |

---

## API Contract

### New Endpoints

#### POST /data-sync
Manually trigger data synchronization from upstream API.
```
POST /data-sync
X-Admin-Token: <token>
Content-Type: application/json

{
  "sync_type": "incremental",  # or "full"
  "limit": 100
}

Response: 202 Accepted
{
  "sync_id": "sync_20240913_001",
  "status": "in_progress",
  "records_processed": 0,
  "eta_seconds": 45
}
```

#### GET /analytics/top-characters
Retrieve most popular characters by request count.
```
GET /analytics/top-characters?limit=20&days=30

Response: 200 OK
{
  "period_days": 30,
  "patterns": [
    {
      "character_id": 1,
      "name": "Rick Sanchez",
      "request_count": 3421,
      "cache_hit_rate": 0.95,
      "avg_latency_ms": 25
    }
  ]
}
```

#### GET /analytics/query-patterns
Retrieve most common query patterns.
```
GET /analytics/query-patterns?limit=10&hours=1

Response: 200 OK
{
  "analysis_window_hours": 1,
  "patterns": [
    {
      "query": "page=1&limit=10",
      "count": 342,
      "cache_hit_rate": 0.92,
      "avg_latency_ms": 18
    }
  ]
}
```

---

## Testing Requirements

- Integration tests with real PostgreSQL instance
- Schema migration tests: Verify forward/rollback capability
- Data sync tests: Incremental vs. full sync correctness
- Race condition tests: Concurrent upserts, no duplicates
- Connection pool tests: Exhaustion scenario, recovery
- Retention policy tests: Old records purged, recent preserved
- Analytics query tests: Correctness and performance under load

---

## Documentation

- Schema diagram and ER model
- Migration guide: How to run/rollback migrations
- Data retention policy: What data is kept and for how long
- Performance tuning: Index strategies, query optimization
- Backup & recovery procedures
