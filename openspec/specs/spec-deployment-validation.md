# Specification: Deployment Validation Workflow

## Overview

This specification defines the GitHub Actions workflow that validates the complete docker-compose stack (PostgreSQL, Redis, and rick-morty-api) to ensure all services start correctly, pass health checks, and communicate properly.

## Trigger Conditions

**Primary Events**:
1. **Push**: To branches `develop`, `master`, `feature/*`
2. **Pull Request**: To branches `develop`, `master`
3. **Workflow Dispatch**: Manual trigger from GitHub Actions UI

**Dependency**: Runs AFTER the main CI pipeline (test job) completes successfully

**Branch Filtering**: 
- Triggered for: `develop`, `master`, feature branches
- NOT triggered for: `main` (if it exists), `release` branches

## Workflow Execution Context

**Environment**:
- **Runner**: ubuntu-latest (Docker pre-installed)
- **Timeout**: 10 minutes
- **Docker Version**: Latest stable

**Pre-requisites**:
- All unit tests passed (from CI pipeline)
- Docker and docker-compose available
- No additional external dependencies

## Workflow Steps

### 1. Checkout Repository
**Scenario**: Access docker-compose.yml and application code
- Uses `actions/checkout@v4`
- Fetch-depth: 1 (only current commit)
- Includes all application source files and docker-compose configuration

### 2. Display Environment Info
**Scenario**: Debug information for troubleshooting
- Print Docker version: `docker --version`
- Print docker-compose version: `docker-compose --version`
- Logged for debugging failed deployments

### 3. Pull Base Images (Optional Pre-fetch)
**Scenario**: Pre-download PostgreSQL and Redis images to reduce startup time
```bash
docker pull postgres:15-alpine
docker pull redis:7-alpine
```
- Optional: Can be skipped if automatic pull during compose works
- Rationale: Pre-fetch ensures images are available; reduces timeout risk

### 4. Start docker-compose Stack
**Scenario**: Spin up all three services (postgres, redis, rick-morty-api)
```bash
docker-compose -f docker-compose.yml up -d
```

**Configuration**:
- All services defined in existing `docker-compose.yml`
- Services started in dependency order:
  1. PostgreSQL (depends on nothing)
  2. Redis (depends on nothing)
  3. rick-morty-api (depends on postgres and redis)
- Network: rick-morty-network (bridge driver)
- Volumes: postgres_data, redis_data (named volumes)

**Expected Output**:
```
Creating network "rick-morty-network" with driver "bridge"
Creating rick-morty-postgres ... done
Creating rick-morty-redis ... done
Creating rick-morty-api ... done
```

### 5. Wait for Services to Be Healthy
**Scenario**: Give services time to initialize and pass health checks
- Initial wait: 30 seconds (allows startup)
- Then check health status every 5 seconds for up to 120 seconds total

**Health Check Validation**:
```bash
docker-compose exec -T postgres pg_isready -U admin -d rickmorty
docker-compose exec -T redis redis-cli ping
curl http://localhost:5000/health
```

**Expected Results**:
- PostgreSQL: "accepting connections" message
- Redis: "PONG" response
- API: HTTP 200 with health status JSON

### 6. Verify Inter-Service Communication
**Scenario**: Confirm services can reach each other via docker network
```bash
# From API container, verify database connectivity
docker-compose exec -T rick-morty-api python -c "
import os
from sqlalchemy import create_engine
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
conn = engine.connect()
print('✅ Database connectivity verified')
conn.close()
"

# From API container, verify Redis connectivity
docker-compose exec -T rick-morty-api python -c "
import os
import redis
redis_url = os.getenv('REDIS_URL')
r = redis.from_url(redis_url)
r.ping()
print('✅ Redis connectivity verified')
"
```

**Expected Output**:
- Database: Connection successful, queries execute
- Redis: Ping returns PONG, set/get operations work

### 7. Run Application Integration Tests
**Scenario**: Execute basic API functionality tests
```bash
docker-compose exec -T rick-morty-api pytest tests/integration/ -v
```

**Test Scope**:
- API endpoint availability
- Database queries work
- Redis caching works
- Data consistency

### 8. Collect Logs and Diagnostics
**Scenario**: Capture logs for debugging if validation fails
```bash
# Collect all service logs
docker-compose logs > docker-compose-logs.txt

# Service-specific logs
docker-compose logs postgres > postgres.log
docker-compose logs redis > redis.log
docker-compose logs rick-morty-api > app.log

# Inspect running containers
docker ps -a
docker inspect rick-morty-postgres
docker inspect rick-morty-redis
docker inspect rick-morty-api
```

### 9. Clean Up Docker Stack
**Scenario**: Remove containers and volumes (runs even if tests fail)
```bash
docker-compose down -v
```

**Cleanup Details**:
- Remove all containers
- Remove named volumes (postgres_data, redis_data)
- Remove network
- Free system resources

### 10. Report Results
**Scenario**: Summary of validation outcome
- If all steps pass: "✅ Deployment Validation Passed"
- If any step fails: "❌ Deployment Validation Failed"
- Links to logs in GitHub Actions artifacts

## Service Configuration Details

### PostgreSQL Service
**Image**: postgres:15-alpine  
**Configuration** (from docker-compose.yml):
```
POSTGRES_USER: admin
POSTGRES_PASSWORD: password
POSTGRES_DB: rickmorty
Port: 5432 (internal), 5432 (host)
```

**Health Check**:
- Command: `pg_isready -U admin -d rickmorty`
- Interval: 10 seconds
- Timeout: 5 seconds
- Retries: 5
- Expected startup: 10-20 seconds

**Data Persistence**: Named volume `postgres_data` (not persisted across runs)

### Redis Service
**Image**: redis:7-alpine  
**Configuration** (from docker-compose.yml):
```
Port: 6379 (internal), 6379 (host)
Command: default redis-server
```

**Health Check**:
- Command: `redis-cli ping`
- Interval: 10 seconds
- Timeout: 5 seconds
- Retries: 5
- Expected startup: 5-10 seconds

**Data Persistence**: Named volume `redis_data` (not persisted across runs)

### rick-morty-api Service
**Image**: Local build from Dockerfile  
**Build Context**: Repository root  
**Configuration** (from docker-compose.yml):
```
DATABASE_URL: postgresql://admin:password@postgres:5432/rickmorty
REDIS_URL: redis://redis:6379/0
FLASK_ENV: production
FLASK_DEBUG: false
Port: 5000 (internal), 5000 (host)
```

**Health Check**:
- Command: `python -c "import requests; requests.get('http://localhost:5000/health')"`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 15 seconds

**Resource Limits**:
- CPU: 0.5 (reserved), 1.0 (limit)
- Memory: 256MB (reserved), 512MB (limit)

**Startup Process**:
1. Execute docker_build_validation.sh (pre-flight checks)
2. Execute init_db.py (database initialization)
3. Start gunicorn with 2 workers
4. Respond to health checks

## Validation Checklist

### Service Startup
- [ ] PostgreSQL container starts without errors
- [ ] PostgreSQL health check passes (pg_isready)
- [ ] Redis container starts without errors
- [ ] Redis health check passes (redis-cli ping)
- [ ] rick-morty-api container starts without errors
- [ ] rick-morty-api health check passes (HTTP /health)

### Network Connectivity
- [ ] API can connect to PostgreSQL (no connection refused)
- [ ] API can connect to Redis (no connection refused)
- [ ] Services reach each other by container name (DNS resolution works)

### Data Layer
- [ ] Database tables created successfully
- [ ] Sample data initialized correctly
- [ ] Redis cache keys set and retrieved
- [ ] Transactions work correctly

### Application Layer
- [ ] API startup script runs without errors
- [ ] API endpoints respond (GET /health)
- [ ] API can query external Rick and Morty API (via caching)
- [ ] API responses are valid JSON

### Resource Usage
- [ ] Each service runs within resource limits
- [ ] No Out-of-Memory errors
- [ ] CPU usage stays reasonable (< 80% during startup)

## Failure Scenarios

| Step | Failure Mode | Likely Cause | Resolution |
|------|--------------|--------------|-----------|
| Pull images | Image not found | Network issue or image deleted | Check internet, verify image names |
| Start postgres | Container exits | Volume permission, port conflict | Check port 5432 free, fix volume permissions |
| Start redis | Container exits | Port conflict | Check port 6379 free |
| Start app | Container exits | Code error, missing dependencies | Check application logs, fix code |
| Health check | Timeout | Service not responding | Check service logs, verify network |
| Database connection | Connection refused | PostgreSQL not ready | Increase health check retries or wait time |
| Redis connection | ECONNREFUSED | Redis not ready or network issue | Check Redis service status |
| API test | Status 500 | Application code error | Check application logs for exception |
| Cleanup | Volume busy | Container still running | Force remove with docker rm -f |

## Performance Requirements

- **Total Execution Time**: < 5 minutes (target), < 10 minutes (max timeout)
- **Service Startup**: < 60 seconds for all services to pass health checks
- **Database Init**: < 30 seconds (init_db.py execution)
- **API Ready**: < 15 seconds after health check passes

**Typical Timeline**:
- Pull images: 30s (if not cached)
- Start services: 60s (database init, API startup)
- Health checks: 30s
- Integration tests: 60s
- Logs collection: 10s
- Cleanup: 20s
- **Total**: ~3 minutes

## Logging and Artifacts

**Logs Saved as Artifacts**:
- `docker-compose-logs.txt` - Complete log output
- `postgres.log` - PostgreSQL logs
- `redis.log` - Redis logs
- `app.log` - Application logs

**Artifact Retention**: 30 days (GitHub Actions default)

**GitHub Actions Output**:
- Console output shows each step
- Passed health checks marked with ✅
- Failed checks marked with ❌
- Links to artifacts for debugging

## Security Considerations

1. **Sensitive Data**:
   - Database password (hardcoded as "password" - test only)
   - Redis has no password (test only)
   - Real deployment would use secrets
   - Logs do not expose database contents

2. **Network Isolation**:
   - Services communicate via private docker network
   - Ports exposed only to localhost (5432, 6379, 5000)
   - External network cannot access services

3. **Data Cleanup**:
   - Volumes removed after each test run
   - No persistent test data left behind
   - Multiple test runs don't interfere

## Acceptance Criteria

1. ✅ Workflow triggers automatically on push/PR to appropriate branches
2. ✅ All three services start without errors
3. ✅ All health checks pass within timeout
4. ✅ Inter-service communication verified (database, Redis)
5. ✅ Integration tests pass against running services
6. ✅ Docker-compose logs captured for debugging
7. ✅ Cleanup removes all containers and volumes
8. ✅ Workflow completes in < 5 minutes under normal conditions
9. ✅ Clear pass/fail status shown in GitHub Actions UI
10. ✅ Logs available in artifacts for failed runs

## Testing Scenarios

### Scenario 1: Successful Deployment
**Given**: Code passes unit tests  
**When**: Push to develop branch  
**Then**:
- Workflow triggers automatically
- All services start and pass health checks
- Integration tests pass
- Workflow shows ✅ status
- Total execution: ~3 minutes

**Verification**:
- GitHub Actions UI shows "Success"
- All steps have green checkmarks
- Logs show "✅ Deployment Validation Passed"

### Scenario 2: Database Connection Failure
**Given**: Application code has SQL syntax error  
**When**: Push includes database query change  
**Then**:
- Services start (postgres, redis, api containers created)
- API container fails health check
- Error logs captured: "ProgrammingError: syntax error"
- Cleanup removes containers
- Workflow shows ❌ status

**Debugging**:
- Download app.log artifact
- Search for error: "ProgrammingError"
- Fix SQL syntax in code
- Push fix to trigger workflow again

### Scenario 3: Redis Integration Failure
**Given**: Cache implementation has bug  
**When**: Integration test attempts to set/get cache  
**Then**:
- Services all start successfully
- Health checks pass
- Integration test fails with Redis error
- Logs show Redis exception
- Workflow shows ❌ status

**Resolution**:
- Fix cache code
- Push to trigger workflow
- Verify fix passes

### Scenario 4: Out of Memory
**Given**: Application has memory leak  
**When**: Services run for extended time  
**Then**:
- Services start but app container exits with OOM
- Health check timeout (container not responding)
- Logs show "Killed: Out of Memory"
- Workflow fails

**Resolution**:
- Fix memory leak in application
- Increase container limits in docker-compose.yml
- Retry workflow

### Scenario 5: Network Timeout (External API)
**Given**: API calls external Rick and Morty API  
**When**: External API is slow or unavailable  
**Then**:
- Services start and health checks pass
- Integration test may timeout on external API call
- Logs show connection timeout
- Test should have fallback/retry logic

**Mitigation**:
- Use timeout for external API calls
- Mock external API in integration tests
- Implement circuit breaker pattern

## Related Specifications

- [Image Build and Push Workflow](spec-docker-build-push.md) - Publishes image to Docker Hub
- Existing: [CI Pipeline](../../.github/workflows/ci.yml) - Unit tests, security checks
- Existing: [CD Pipeline](../../.github/workflows/cd.yml) - Production deployment
