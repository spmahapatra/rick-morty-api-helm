# Specification: Automated Image Build and Push Workflow

## Overview

This specification defines the GitHub Actions workflow that automatically builds the `rick-morty-api` Docker image and publishes it to Docker Hub when a semantic version tag is created.

## Trigger Conditions

**Event Type**: `create` event with `ref_type: tag`

**Tag Format Requirements**:
- Pattern: `v{major}.{minor}.{patch}[-{prerelease}]`
- Examples: `v1.0.0`, `v2.1.0`, `v1.0.0-beta`, `v1.0.0-rc.1`
- Validation: Must match regex `^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$`

**Branch Independence**: Triggered regardless of branch; tag alone determines image build

## Workflow Steps

### 1. Tag Validation
**Scenario**: Developer creates tag `v1.5.0`
- Extract tag name from `github.ref`
- Validate semantic version format
- Error handling: Non-matching tags are rejected with clear message
- Output: Tag name passed to downstream jobs

### 2. Checkout Repository
**Scenario**: Access source code and Dockerfile
- Uses `actions/checkout@v4`
- Fetch-depth: 1 (only current commit needed, no history)
- Includes all files needed for docker build (app.py, src/, requirements.txt, Dockerfile, scripts)

### 3. Set up Docker Buildx
**Scenario**: Enable BuildKit features for layer caching and multi-platform builds
- Uses `docker/setup-buildx-action@v2`
- Enables efficient builds with GitHub Actions cache

### 4. Docker Hub Authentication
**Scenario**: Authenticate to Docker Hub for image push
- Uses `docker/login-action@v2`
- Registry: docker.io (Docker Hub)
- Username: `${{ secrets.DOCKERHUB_USERNAME }}`
- Password: `${{ secrets.DOCKERHUB_TOKEN }}`
- Pre-requisite: Secrets must be configured in GitHub repository settings

### 5. Extract Build Metadata
**Scenario**: Generate image tags and labels
- Uses `docker/metadata-action@v4`
- Tags to generate:
  - `latest` tag (if on default branch OR all tags)
  - Semantic version: `1.5.0` (from tag)
  - Major.minor: `1.5` (from tag)
  - Commit SHA prefix: `{branch}-{sha7}` (for debugging)
- Labels include:
  - git.revision (commit SHA)
  - git.ref (tag name)
  - org.opencontainers.image.version
  - org.opencontainers.image.created (timestamp)

### 6. Build and Push Docker Image
**Scenario**: Compile Dockerfile and publish to Docker Hub
- Uses `docker/build-push-action@v4`
- Context: `.` (repository root)
- Dockerfile: `Dockerfile` (default location)
- Push: `true` (enabled for successful builds)
- Tags: Generated from metadata step
- Labels: Generated from metadata step
- Cache:
  - From: `type=registry,ref=docker.io/${{ DOCKERHUB_USERNAME }}/rick-morty-api:buildcache`
  - To: Same location with `mode=max` for layer reuse
- Build Args: None required (all configured via environment in docker-compose)
- Buildx output: Image digest captured for verification

## Image Specifications

### Image Name Format
```
docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:{tag}
```

### Published Tags
For tag `v1.5.0`:
1. `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.5.0` (exact version)
2. `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.5` (major.minor)
3. `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:latest` (always latest)

For tag `v1.5.0-beta`:
1. `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.5.0-beta` (exact prerelease)
2. `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:latest` (includes prerelease)

### Image Compatibility

**Base Image**: `python:3.9-slim` (from Dockerfile line 1)
- **Platform Support**: linux/amd64, linux/arm64 (via Buildx multi-platform)
- **Size Target**: < 200MB (slim variant used)
- **Non-root User**: appuser (UID 1000) for security

**Environment Variables** (configurable at runtime):
- `FLASK_ENV`: production/development
- `FLASK_DEBUG`: true/false
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `LOG_FORMAT`: json/text
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR

**Health Check**: 
- Command: Python requests to `/health` endpoint
- Interval: 30s
- Timeout: 10s
- Retries: 3
- Start period: 5s

**Port Exposure**: 5000 (EXPOSE directive in Dockerfile)

**Entry Point**:
```bash
sh -c "./docker_build_validation.sh && python init_db.py && gunicorn -w 2 -b 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - app:app"
```

## Dependencies and Exclusions

### What IS Built
- **rick-morty-api**: Custom application image
- Dependencies: Installed via requirements.txt

### What IS NOT Built (External Dependencies)
- **PostgreSQL**: Pull `postgres:15-alpine` from Docker Hub (docker-compose.yml handles this)
- **Redis**: Pull `redis:7-alpine` from Docker Hub (docker-compose.yml handles this)

Rationale: These are stable, official images; rebuilding adds no value and increases build time.

## Security Considerations

1. **Credentials**: Uses GitHub Actions secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
   - Never logged or exposed in output
   - Revocable from Docker Hub dashboard
   
2. **Layer Scanning**: Build happens on GitHub Actions (Microsoft-hosted runners)
   - No malicious code injection in build environment
   
3. **Non-root Execution**: Container runs as appuser (UID 1000)
   - Prevents privilege escalation attacks
   
4. **Minimal Base Image**: python:3.9-slim chosen over full python:3.9
   - Reduces attack surface
   - Fewer packages = fewer CVEs

5. **Build Cache Invalidation**: Automatic on dependency changes
   - requirements.txt change triggers full rebuild

## Failure Scenarios and Recovery

| Scenario | Cause | Recovery |
|----------|-------|----------|
| Tag validation fails | Invalid semver format | Use correct format: `v1.2.3` |
| Docker Hub auth fails | Invalid credentials | Update DOCKERHUB_TOKEN secret |
| Build fails | Syntax error in code | Fix code, create new tag (old tag remains) |
| Push fails | Network timeout | Retry workflow from GitHub Actions UI |
| Health check fails | App error at startup | Check application logs in workflow output |

## Performance Requirements

- **Build Time Target**: < 10 minutes
- **Build Cache Reuse**: Layer cache persists across builds (registry-based)
- **Storage**: Each image version retained on Docker Hub (manual cleanup if needed)
- **Bandwidth**: Acceptable for GitHub Actions (no rate limiting expected)

## Acceptance Criteria

1. ✅ Workflow triggered automatically on semantic version tag creation
2. ✅ Image built using existing Dockerfile without modifications
3. ✅ Image successfully pushed to Docker Hub (DOCKERHUB_USERNAME/rick-morty-api)
4. ✅ Three tags created: version, major.minor, latest
5. ✅ Image deployable to docker-compose without any modifications
6. ✅ Image deployable to Kubernetes via Helm charts (no code changes needed)
7. ✅ Build logs show build time, layers cached, image digest
8. ✅ No errors in GitHub Actions workflow execution
9. ✅ Image accessible via `docker pull docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.2.3`
10. ✅ Validation confirms image runs health check successfully

## Testing Scenarios

### Scenario 1: Create Standard Release
**Given**: Development on `develop` branch with latest code  
**When**: Developer creates tag `v1.0.0`  
**Then**:
- Workflow triggers automatically
- Image builds successfully (< 10 min)
- Image published to Docker Hub with tags: `latest`, `1.0.0`, `1.0`
- Tag in GitHub shows "Release" status

**Verification**:
```bash
docker pull docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.0.0
docker run --rm docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.0.0 --version
```

### Scenario 2: Create Pre-release
**Given**: Development branch with experimental feature  
**When**: Developer creates tag `v1.5.0-beta.1`  
**Then**:
- Workflow triggers automatically
- Image published with tag: `1.5.0-beta.1`
- `latest` tag updated to pre-release

**Verification**:
```bash
docker pull docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.5.0-beta.1
docker inspect docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:latest | grep -i version
```

### Scenario 3: Build Failure Recovery
**Given**: Tag `v1.6.0` created with broken code  
**When**: Workflow build fails  
**Then**:
- Image NOT pushed to Docker Hub
- GitHub Actions UI shows failure with logs
- Tag remains in Git history (not deleted)
- Developer can fix code and create new tag `v1.6.1`

**Recovery Steps**:
1. Fix code locally
2. Push fix to repository
3. Create new semantic version tag
4. Workflow runs again with fixed code

### Scenario 4: Use in docker-compose
**Given**: Image published to Docker Hub  
**When**: Local developer runs `docker-compose up`  
**Then**:
- docker-compose.yml references: `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:latest`
- Image pulled from Docker Hub instead of building locally
- All three services (postgres, redis, api) start correctly
- Health checks pass within 30s

### Scenario 5: Use in Helm Deployment
**Given**: Image published to Docker Hub  
**When**: Kubernetes cluster deployed with Helm chart  
**Then**:
- Helm values.yaml references: `docker.io/{DOCKERHUB_USERNAME}/rick-morty-api:1.0.0`
- Image pulled from Docker Hub
- Pod starts, passes readiness/liveness probes
- Service endpoints respond to requests

## Related Specifications

- [Deployment Validation Workflow](spec-deployment-validation.md) - Validates docker-compose stack on every push
- Existing: [CI Pipeline](../../.github/workflows/ci.yml) - Unit tests, security checks, linting
- Existing: [CD Pipeline](../../.github/workflows/cd.yml) - Production deployment orchestration
