# Technical Design: CI/CD Docker Hub and Deployment Validation Workflows

## Architecture Overview

```
                     ┌─────────────────────────────────────┐
                     │       GitHub Repository             │
                     │   (commits, branches, tags)         │
                     └──────────┬──────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
          ┌─────────▼──────────┐   ┌───────▼──────────┐
          │  CI Pipeline       │   │  Tag Push Event  │
          │ (ci.yml)           │   │                  │
          │                    │   │ v1.2.3 tag      │
          │ • Lint             │   │ created         │
          │ • Unit Tests       │   │                  │
          │ • Security Scans   │   └────────┬─────────┘
          │ • Build validation │            │
          └────────┬───────────┘            │
                   │                        │
                   ├─► Passes ──────────────┤
                   │                        │
                   │          ┌─────────────▼─────────────┐
                   │          │  NEW: Image Build & Push  │
                   │          │  Workflow (image-build.yml)
                   │          │                           │
                   │          │ • Validate semver tag      │
                   │          │ • Build Dockerfile        │
                   │          │ • Push to Docker Hub      │
                   │          │ • Tags: v1.2.3, 1.2, latest
                   │          └──────────┬────────────────┘
                   │                     │
                   │                     ▼
                   │          ┌──────────────────────┐
                   │          │  Docker Hub Registry │
                   │          │ /rick-morty-api:    │
                   │          │  - latest            │
                   │          │  - 1.2.3             │
                   │          │  - 1.2               │
                   │          │  - buildcache        │
                   │          └──────────┬───────────┘
                   │                     │
                   ├────────────────────────────────────┐
                   │                                    │
          ┌────────▼────────────────┐      ┌───────────▼────────────┐
          │ NEW: Deploy Validation  │      │  CD Pipeline (cd.yml)  │
          │ Workflow (validate.yml) │      │                        │
          │                         │      │ • Deploy to Staging    │
          │ • Pull base images      │      │ • Deploy to Prod       │
          │ • docker-compose up     │      │ • Health checks        │
          │ • Health checks         │      │ • Smoke tests          │
          │ • Integration tests     │      │ • Notifications        │
          │ • docker-compose down   │      └────────────────────────┘
          └──────┬──────────────────┘
                 │
                 ▼
          ✅ Pass/❌ Fail Status
          (shown in GitHub UI)
```

## Workflow Interaction Flow

### Flow 1: Release Process (Image Build & Push)
```
Developer creates semantic version tag
    ↓
GitHub triggers "create" event
    ↓
workflow: image-build.yml starts
    ├─► Job: verify-tag-creation
    │   ├─ Extract tag name (v1.2.3)
    │   └─ Validate semver format
    │       └─ If invalid: Fail with error message
    │
    ├─► Job: build-and-test (if validation passed)
    │   ├─ Checkout code
    │   ├─ Login to Docker Hub
    │   ├─ Build image using Dockerfile
    │   ├─ Push to docker.io/DOCKERHUB_USERNAME/rick-morty-api:1.2.3
    │   └─ Generate cache layers
    │
    └─► Result: Image published to Docker Hub
        └─ Accessible to: Local dev, Helm deployments, CI/CD systems
```

### Flow 2: Deployment Validation (Every Push)
```
Developer pushes to develop/master/feature/*
    ↓
GitHub triggers CI pipeline (ci.yml)
    ├─ Unit tests, linting, security scans
    ├─ If all pass...
    │
    └─► workflow: validate.yml starts (needs: [test])
        ├─► Job: deployment-validation
        │   ├─ Checkout code
        │   ├─ Pull postgres:15-alpine
        │   ├─ Pull redis:7-alpine
        │   ├─ docker-compose up (builds rick-morty-api locally)
        │   ├─ Wait for health checks
        │   ├─ Verify inter-service communication
        │   ├─ Run integration tests
        │   ├─ Collect logs
        │   └─ docker-compose down
        │
        └─► Result: ✅ Pass or ❌ Fail
            └─ Shown in GitHub Actions UI
```

## File Structure

```
.github/
├── workflows/
│   ├── ci.yml                        (existing - lint, test, security)
│   ├── cd.yml                        (existing - production deployment)
│   ├── image-build.yml               (NEW - tag trigger → Docker Hub push)
│   └── deployment-validation.yml     (NEW - push trigger → docker-compose validate)
│
├── agents/
│   └── blueprint-code-agent.yaml     (existing - copilot setup)
│
docker-compose.yml                    (existing - service definitions)
Dockerfile                            (existing - app image definition)
requirements.txt                      (existing - Python dependencies)
app.py                                (existing - Flask application)
init_db.py                            (existing - database initialization)
docker_build_validation.sh            (existing - pre-flight checks)
```

## Configuration: image-build.yml

### Trigger Configuration
```yaml
on:
  create:
    tags: [ 'v*' ]  # Only on tag creation events
  workflow_dispatch: # Allow manual trigger for debugging
```

### Job Dependencies
- No dependencies (runs independently on tag push)
- Parallel execution: All jobs can run concurrently

### Docker Hub Integration
**Secrets Required**:
- `DOCKERHUB_USERNAME` - Docker Hub account username
- `DOCKERHUB_TOKEN` - Docker Hub personal access token (not password)

**Token Requirements**:
- Type: Personal Access Token (PAT)
- Permissions: Read/Write for repos
- Scope: Full control recommended
- Created in Docker Hub dashboard: Settings → Security → New Access Token

### Image Naming
```
Registry: docker.io (implicit for Docker Hub)
Namespace: DOCKERHUB_USERNAME (variable from secret)
Repository: rick-morty-api
Tags:
  - latest (always updated)
  - {major}.{minor}.{patch} (from tag)
  - {major}.{minor} (derived)
  - buildcache (for layer reuse)
```

### Cache Strategy
```yaml
cache-from: type=registry,ref=docker.io/${{ DOCKERHUB_USERNAME }}/rick-morty-api:buildcache
cache-to: type=registry,ref=docker.io/${{ DOCKERHUB_USERNAME }}/rick-morty-api:buildcache,mode=max
```

Benefits:
- Layer caching across builds (faster rebuild)
- buildcache tag never used for runtime (hidden tag)
- Automatic cache invalidation on dependency changes

### Build Process
```
1. Checkout repository (shallow clone, current commit only)
2. Set up Docker Buildx with builder instance
3. Authenticate to Docker Hub (docker/login-action)
4. Extract metadata (tags, labels, versions)
5. Build image:
   - FROM python:3.9-slim (base image)
   - COPY requirements.txt
   - RUN pip install
   - COPY application files
   - HEALTHCHECK directive
   - USER appuser (non-root)
6. Push to Docker Hub
7. Output image digest for verification
```

## Configuration: deployment-validation.yml

### Trigger Configuration
```yaml
on:
  push:
    branches: [ develop, master, feature/* ]
  pull_request:
    branches: [ develop, master ]
  workflow_dispatch:

needs: [test]  # Wait for CI pipeline tests to pass
```

### Service Orchestration
**docker-compose.yml Integration**:
- Uses existing configuration (no modifications needed)
- Services in execution order:
  1. PostgreSQL (port 5432)
  2. Redis (port 6379)
  3. rick-morty-api (port 5000, depends on 1&2)

**Network Model**:
- Internal docker network: rick-morty-network (bridge)
- Services reach each other by container name (DNS resolution)
- Only localhost can access ports (5432, 6379, 5000)

### Health Check Strategy
```
Phase 1: Service Startup (60 seconds)
  - docker-compose up -d
  - Services initialize, health checks start running

Phase 2: Health Check Verification (120 seconds max)
  - Poll each service every 5 seconds
  - PostgreSQL: pg_isready
  - Redis: redis-cli ping
  - API: curl http://localhost:5000/health

Phase 3: Integration Testing (60 seconds)
  - Database operations
  - Redis caching operations
  - API endpoint tests

Phase 4: Cleanup (20 seconds)
  - docker-compose down -v (remove volumes)
  - Free resources
```

### Logging and Diagnostics
```
Captured Automatically:
  ✓ GitHub Actions console output
  ✓ docker-compose logs (all services combined)
  ✓ Service-specific logs (postgres.log, redis.log, app.log)
  ✓ Container inspect output (images, ports, environment)
  ✓ Docker ps (container listing)

Storage:
  - Artifacts: 30-day retention (configurable)
  - Console: Searchable in GitHub Actions UI
  - Accessible to: Project maintainers, CI admin
```

## Technology Stack

### Existing Technologies (Leveraged)
- **Python 3.9** - Application runtime
- **Flask** - Web framework
- **PostgreSQL 15** - Database
- **Redis 7** - Cache layer
- **Docker** - Container platform
- **docker-compose** - Orchestration (local/testing)
- **Gunicorn** - WSGI application server
- **GitHub Actions** - CI/CD platform

### New Technologies (Added)
- **Docker Buildx** - Advanced image building with cache
- **Docker Hub Registry** - Public image repository
- **GitHub Secrets** - Secure credential storage

### Existing GitHub Actions Actions Used
- `actions/checkout@v4` - Repository access
- `docker/setup-buildx-action@v2` - Docker BuildKit setup
- `docker/login-action@v2` - Registry authentication
- `docker/metadata-action@v4` - Tag/label generation
- `docker/build-push-action@v4` - Build and push

## Trade-offs and Decisions

### Decision 1: Publish to Docker Hub Instead of GitHub Container Registry
**Alternatives**:
1. GitHub Container Registry (ghcr.io)
2. Private Docker Hub registry
3. Self-hosted registry (Harbor, Artifactory)

**Chosen**: Docker Hub (Public)
**Reasoning**:
- Existing secrets already configured (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- Wider team access (no GitHub repo access required)
- No additional infrastructure
- Free public registry tier
- Industry standard for image distribution

**Trade-off**:
- (+) Accessible to anyone with Docker
- (+) No GitHub-specific credentials needed
- (-) Public image (could be mitigated with private Docker Hub repo)

### Decision 2: Build Only App Image, Pull Postgres/Redis
**Alternatives**:
1. Build all three images (postgres, redis, app)
2. Pull all from public registries
3. Build postgres/redis from source

**Chosen**: Build app only, pull postgres/redis from public registries
**Reasoning**:
- PostgreSQL and Redis are stable, don't change with app versions
- Official Docker images are well-maintained and secure
- Building them adds time without benefit
- Compatible with Kubernetes deployments (same base images)

**Trade-off**:
- (+) Faster builds (5-10 min instead of 15-20 min)
- (+) Smaller image size (app-only image ~150MB vs 500MB for all three)
- (-) Requires internet access to pull base images
- (-) External dependency on Docker Hub availability

### Decision 3: Validate on Every Push, Build on Tag Only
**Alternatives**:
1. Validate and build on every push (slower CI)
2. Validate on PR, build on merge (missing validation before merge)
3. Manual build trigger only (no automation)

**Chosen**: Validate every push, build on tag only
**Reasoning**:
- Developers get fast feedback (validation < 5 min)
- Release artifact only created on intentional tag
- Avoids cluttering Docker Hub with experimental images
- Follows GitOps principles (tags as release markers)

**Trade-off**:
- (+) CI feedback is fast
- (+) Only released versions published
- (-) Extra workflow file to maintain

### Decision 4: Use Semver Tag Validation
**Alternatives**:
1. Accept any tag format (v1, release-2023-09-13, custom-build)
2. Only major.minor.patch (no pre-releases)
3. Custom tagging scheme (e.g., build-{number})

**Chosen**: Semantic versioning with optional pre-release (v1.2.3 or v1.2.3-beta)
**Reasoning**:
- Industry standard (follows semver.org)
- Communicates intent (major = breaking changes)
- Docker image tags follow same convention
- Kubernetes/Helm expect semver versions
- Sorting and comparison work correctly

**Trade-off**:
- (+) Clear version semantics
- (+) Helm compatibility
- (-) Enforces discipline in versioning
- (-) Pre-releases require extra syntax (-beta, -rc)

## Security Architecture

### Credential Management
```
Secrets (GitHub):
  DOCKERHUB_USERNAME ──► [Secret Store] ──► Used at: docker/login-action
  DOCKERHUB_TOKEN    ──► [Secret Store] ──► Used at: docker/login-action
                                              Never logged or exposed

Notes:
  • Secrets never appear in logs
  • Secrets masked in GitHub Actions output (shown as ***)
  • Token revocable without code changes
  • Personal Access Token used instead of password
  • Token limited to Docker Hub API only
```

### Image Security
```
Build Environment:
  ✓ Runs on GitHub's hosted runners (Microsoft-managed infrastructure)
  ✓ Ephemeral environment (new runner for each build)
  ✓ No long-lived build servers

Image Hardening:
  ✓ Non-root user (appuser, UID 1000) - prevents privilege escalation
  ✓ Slim base image (python:3.9-slim) - minimal attack surface
  ✓ No privileged container capabilities
  ✓ Health checks validate runtime
  ✓ No hardcoded secrets in image layers

Dependency Management:
  ✓ requirements.txt pinned versions (reproducible builds)
  ✓ Base image pinned (python:3.9-slim, not :latest)
  ✓ Docker Hub images scanned by Docker (optional)
  ✓ GitHub Advanced Security can scan images (enterprise feature)
```

### Network Security
```
Deployment Validation:
  ✓ Services communicate via private docker network (rick-morty-network)
  ✓ No external network exposure during testing
  ✓ Ports exposed only to localhost (CI runner)
  ✓ Database credentials hardcoded as test-only (no production secrets)

Production Considerations:
  ✓ This workflow doesn't directly touch production
  ✓ Production deployment (cd.yml) is separate
  ✓ Production requires manual approval (environment-based)
  ✓ Credentials for production should be separate
```

## Observability and Monitoring

### GitHub Actions Integration
```
Workflow Status:
  • Real-time execution in GitHub Actions UI
  • Per-step success/failure indicators
  • Timing information (step duration)
  • Environment variables visible (non-secret)

Log Aggregation:
  • Complete run logs searchable in GitHub
  • Per-job and per-step breakdown
  • Annotation support for test results
  • Error messages highlighted in red

Artifacts:
  • docker-compose-logs.txt (all service logs)
  • Service-specific logs (postgres.log, redis.log, app.log)
  • Inspection outputs (docker ps, docker inspect)
  • Retention: 30 days by default (configurable)
```

### Metrics and Alerts
```
Current State: Manual review via GitHub UI
  
Recommended Enhancements:
  • Slack notifications on build failure
  • Email alerts for failed deployments
  • Metrics dashboard (build time, success rate)
  • Historical trend analysis
  • Alert on release delays
```

## Backwards Compatibility

### Existing Workflows Not Affected
- **ci.yml** (CI Pipeline) - Unchanged
  - Still runs on push/PR
  - Lint, test, security checks continue
  
- **cd.yml** (CD Pipeline) - Unchanged
  - Still triggered on semantic version tags
  - Deployment approval process unchanged
  
- **copilot-setup-steps.yml** - Unchanged
  - GitHub Copilot coding agent integration

### docker-compose.yml Changes
**Breaking Changes**: None. Current file is used as-is.

**Optional Enhancement** (not required):
```yaml
# Current (works as-is):
rick-morty-api:
  build:
    context: .
    dockerfile: Dockerfile

# Could optionally change to (after images published):
rick-morty-api:
  image: docker.io/${DOCKERHUB_USERNAME}/rick-morty-api:latest
  # OR for development keep as build:
```

This allows docker-compose to use published images for faster local development, but the build option still works.

## Deployment Modes

### Mode 1: Local Development
```
Developer workflow:
  $ git clone repo
  $ docker-compose up
  
Behavior:
  • Services built locally (no pre-built images)
  • Initial build slower, subsequent runs use cache
  • Can modify code and rebuild with docker-compose
  • Full control over image customization
```

### Mode 2: Team Collaboration
```
After workflow creates docker-compose changes:
  $ docker-compose up
  
Behavior:
  • Pulls pre-built image from Docker Hub
  • Faster startup (no build step)
  • Consistent images across team
  • Requires internet access to Docker Hub
```

### Mode 3: Kubernetes/Helm
```
Helm deployment:
  helm install rick-morty docker-helm-chart/ \
    --set image.registry=docker.io \
    --set image.repository=DOCKERHUB_USERNAME/rick-morty-api \
    --set image.tag=1.2.3
  
Behavior:
  • Kubernetes pulls image from Docker Hub
  • Same image used in CI, dev, production
  • No build step on K8s cluster
  • Faster pod startup
```

## Failure Recovery and Rollback

### Scenario 1: Bad Release (Broken Image Published)
```
Problem: Tag v1.2.3 pushed, image built, but app doesn't work
Recovery:
  1. Delete tag locally: git tag -d v1.2.3
  2. Delete tag remotely: git push origin --delete v1.2.3
  3. Delete Docker Hub image: docker.io/user/rick-morty-api:1.2.3 (manual)
  4. Fix code
  5. Re-tag with same version OR create new version v1.2.4
  
Prevention:
  • Ensure all tests pass before tagging
  • Test locally with tag before pushing
  • Use pre-release tags (v1.2.3-beta) for testing
```

### Scenario 2: Deployment Validation Fails
```
Problem: Validation workflow shows ❌, services don't start
Recovery:
  1. Review logs in GitHub Actions artifacts
  2. Find root cause (database error, Redis issue, app bug)
  3. Fix issue locally
  4. Push fix (triggers validation again)
  5. Repeat until ✅ passes
  
No production impact:
  • Validation doesn't affect existing deployments
  • Existing production runs on previous image
  • New release blocked until validation passes
```

### Scenario 3: Docker Hub Unavailable
```
Problem: Push to Docker Hub fails (network, maintenance)
Recovery:
  1. GitHub Actions shows build step failed
  2. Fix (wait for Docker Hub availability)
  3. Manual retry: GitHub Actions UI → Workflow → Re-run failed jobs
  4. OR push same tag again (requires removing old tag first)
  
Failover option:
  • Use alternative registry (ghcr.io) temporarily
  • Update secrets and try again
  • Consider multi-registry push for critical releases
```

## Recommended Enhancements

### Phase 2 (Future Improvements)
1. **Multi-registry Publishing**: Push to both Docker Hub and ghcr.io
2. **Image Scanning**: Run Trivy or similar for security vulnerabilities
3. **Release Notes**: Auto-generate from commit messages
4. **Notification System**: Slack alerts on release or failure
5. **Helm Chart Automation**: Auto-update chart version on image release

### Phase 3 (Advanced)
1. **Canary Deployment**: Gradual rollout to Kubernetes
2. **Blue-Green Deployment**: Zero-downtime releases
3. **Performance Testing**: Automated performance regression detection
4. **End-to-End Testing**: Real browser testing with deployed app
5. **Metrics Dashboard**: Build time, success rate, deployment frequency trends

## Implementation Checklist

- [ ] Create `.github/workflows/image-build.yml` file
- [ ] Create `.github/workflows/deployment-validation.yml` file
- [ ] Verify DOCKERHUB_USERNAME secret exists in GitHub repo
- [ ] Verify DOCKERHUB_TOKEN secret exists in GitHub repo
- [ ] Test image-build.yml with manual tag creation
- [ ] Verify image appears in Docker Hub
- [ ] Test deployment-validation.yml on push to develop
- [ ] Verify all services start and pass health checks
- [ ] Test failure scenarios (broken database, redis timeout, etc.)
- [ ] Update documentation (README, contributing guide)
- [ ] Add examples to team wiki/documentation
- [ ] Monitor workflows for first week of production use
- [ ] Collect feedback and iterate on design
