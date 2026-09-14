# Specification: CI/CD Docker Hub and Deployment Validation Workflows

## Overview

This specification defines two GitHub Actions workflows that enhance the automated deployment pipeline for the Rick & Morty API application:

1. **Docker Hub Build and Push Workflow** - Triggered on git tag creation, builds and publishes the `rick-morty-api` Docker image to Docker Hub
2. **Deployment Validation Workflow** - Executes full docker-compose compilation and integration testing to ensure end-to-end deployment readiness

## Change Metadata

- **Change ID:** `ci-cd-dockerhub-workflow`
- **Archive Date:** 2026-09-14
- **Status:** ✅ Formalized & Archived
- **Priority:** High

## Capability Summary

### Workflow 1: Docker Hub Build and Push (`cd-docker-hub-build-push-tag-on-demand.yml`)

**Trigger**: Git tag creation matching semantic versioning pattern `v*.*.*`

**Purpose**: Automatically build and publish the application Docker image to Docker Hub for team distribution and Kubernetes deployments.

**Key Features**:
- Semantic version tag validation (`v1.0.0`, `v1.0.0-beta`, `v2.1.0-rc.1`)
- Multi-platform image builds (linux/amd64, linux/arm64)
- Layer caching via Docker Hub registry cache
- Automatic tag generation: `latest`, `{version}`, `{major}.{minor}`
- Manual workflow dispatch support for debugging

**Image Specifications**:
```
Registry: docker.io (Docker Hub)
Repository: {DOCKERHUB_USERNAME}/rick-morty-api
Tags:
  - latest (always updated)
  - 1.2.3 (exact semantic version)
  - 1.2 (major.minor)
  - buildcache (layer cache, hidden tag)
```

**Base Image**: `python:3.9-slim`
- Non-root user: `appuser` (UID 1000)
- Health check: HTTP `/health` endpoint
- Port: 5000
- Platforms: linux/amd64, linux/arm64

### Workflow 2: Deployment Validation (`cd-deployment-validation-multi-per-commit.yml`)

**Trigger**: Push to `develop`, `master`, `feature/*` branches and PRs to `develop`, `master`

**Purpose**: Validate the complete docker-compose stack before deployment to ensure all services start correctly, pass health checks, and communicate properly.

**Services Validated**:
1. **PostgreSQL** (postgres:15-alpine) - Port 5432
2. **Redis** (redis:7-alpine) - Port 6379
3. **rick-morty-api** (local build) - Port 5000

**Validation Steps**:
1. Checkout repository
2. Display Docker environment info
3. Pre-fetch base images (postgres, redis)
4. Start docker-compose stack
5. Verify PostgreSQL health (`pg_isready`)
6. Verify Redis health (`redis-cli ping`)
7. Verify API health (HTTP 200 on `/health`)
8. Verify inter-service communication (DB & Redis from API container)
9. Run integration tests (if available)
10. Collect diagnostic logs
11. Upload logs as artifacts (7-day retention)
12. Clean up docker-compose stack

**Performance Targets**:
- Total execution: < 5 minutes (target), < 15 minutes (max timeout)
- Service startup: < 60 seconds for all services
- Health checks: 120 seconds max wait time (24 attempts × 5 seconds)

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                        │
│              (commits, branches, tags)                      │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌───────▼──────────┐
│ CI Pipeline │ │  Tag Push Event  │
│  (ci.yml)   │ │                  │
│             │ │ v1.2.3 tag       │
│ • Lint      │ │ created          │
│ • Unit Tests│ └────────┬─────────┘
│ • Security  │          │
└──────┬──────┘          │
       │                 │
       │    ┌────────────▼────────────┐
       │    │  NEW: Docker Hub Build  │
       │    │  & Push Workflow        │
       │    │                         │
       │    │ • Validate semver tag   │
       │    │ • Build Dockerfile      │
       │    │ • Push to Docker Hub    │
       │    │ • Tags: v1.2.3, 1.2,    │
       │    │   latest, buildcache    │
       │    └──────────┬──────────────┘
       │               │
       │               ▼
       │    ┌──────────────────────┐
       │    │  Docker Hub Registry │
       │    │ /rick-morty-api:     │
       │    │  - latest            │
       │    │  - 1.2.3             │
       │    │  - 1.2               │
       │    │  - buildcache        │
       │    └──────────┬───────────┘
       │               │
       ├───────────────┼────────────────────────────────┐
       │               │                                │
┌──────▼──────────────▼─┐    ┌────────────────────────┐  │
│ Deployment Validation │    │  CD Pipeline (cd.yml)  │  │
│ Workflow              │    │                        │  │
│                       │    │ • Deploy to Staging    │  │
│ • Pull base images    │    │ • Deploy to Prod       │  │
│ • docker-compose up   │    │ • Health checks        │  │
│ • Health checks       │    │ • Smoke tests          │  │
│ • Integration tests   │    │ • Notifications        │  │
│ • docker-compose down │    └────────────────────────┘  │
└────────┬──────────────┘
         │
         ▼
  ✅ Pass/❌ Fail Status
  (shown in GitHub UI)
```

## Configuration Details

### Docker Hub Build Workflow (`cd-docker-hub-build-push-tag-on-demand.yml`)

**Triggers**:
```yaml
on:
  create:
    tags: ['v*']
  workflow_dispatch:
    inputs:
      tag_name:
        description: 'Optional: Override tag name for manual run'
        required: false
        type: string
```

**Jobs**:
1. **verify-tag**: Validates semantic version format, extracts version components
2. **build-and-push**: Builds and pushes multi-platform image with cache
3. **notify-success**: Reports successful build
4. **notify-failure**: Reports build failure

**Required Secrets**:
- `DOCKERHUB_USERNAME`: Docker Hub account username
- `DOCKERHUB_TOKEN`: Docker Hub personal access token (PAT)

**Cache Strategy**:
```yaml
cache-from: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/rick-morty-api:buildcache
cache-to: type=registry,ref=docker.io/${{ secrets.DOCKERHUB_USERNAME }}/rick-morty-api:buildcache,mode=max
```

### Deployment Validation Workflow (`cd-deployment-validation-multi-per-commit.yml`)

**Triggers**:
```yaml
on:
  push:
    branches: [develop, master, feature/*]
  pull_request:
    branches: [develop, master]
  workflow_dispatch:
```

**Environment Variables**:
```yaml
env:
  COMPOSE_FILE: docker-compose.yml
  DOCKER_BUILDKIT: 1
  COMPOSE_DOCKER_CLI_BUILD: 1
```

**Health Check Commands**:
- PostgreSQL: `docker compose exec -T postgres pg_isready -U admin -d rickmorty`
- Redis: `docker compose exec -T redis redis-cli ping`
- API: `curl -s http://localhost:5000/health` (expects HTTP 200)

**Inter-Service Verification**:
- Database connectivity from API container via SQLAlchemy
- Redis connectivity from API container via redis-py

**Logs Collection** (always runs):
- `deployment-logs/docker-compose.log` - All services combined
- `deployment-logs/postgres.log` - PostgreSQL specific
- `deployment-logs/redis.log` - Redis specific
- `deployment-logs/rick-morty-api.log` - API specific
- `deployment-logs/docker-ps.txt` - Container listing

## Deployment Modes

### Mode 1: Local Development
```bash
docker-compose up
```
- Services built locally
- Full control over image customization
- Initial build slower, subsequent runs use cache

### Mode 2: Team Collaboration (Using Published Images)
```bash
docker-compose up
```
- Pulls pre-built image from Docker Hub
- Faster startup (no build step)
- Consistent images across team
- Requires docker-compose.yml to reference published image

### Mode 3: Kubernetes/Helm
```bash
helm install rick-morty docker-helm-chart/ \
  --set image.registry=docker.io \
  --set image.repository=DOCKERHUB_USERNAME/rick-morty-api \
  --set image.tag=1.2.3
```
- Kubernetes pulls image from Docker Hub
- Same image used in CI, dev, production
- No build step on K8s cluster
- Faster pod startup

## Security Architecture

### Credential Management
- GitHub Actions secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- Never logged or exposed in output
- Token revocable from Docker Hub dashboard
- Personal Access Token used (not password)

### Image Hardening
- Non-root user (`appuser`, UID 1000) - prevents privilege escalation
- Slim base image (`python:3.9-slim`) - minimal attack surface
- No privileged container capabilities
- Health checks validate runtime
- No hardcoded secrets in image layers

### Network Security (Validation Workflow)
- Services communicate via private docker network (`rick-morty-network`)
- Ports exposed only to localhost (CI runner)
- Database credentials hardcoded as test-only (no production secrets)
- Volumes removed after each test run (`docker-compose down -v`)

## Acceptance Criteria

### Docker Hub Build Workflow
- ✅ Tag creation with `v1.2.3` format triggers Docker Hub build
- ✅ Docker image successfully published to `DOCKERHUB_USERNAME/rick-morty-api:1.2.3` and `:latest`
- ✅ Multi-platform image (amd64, arm64) built
- ✅ Image deployable to both local docker-compose and Kubernetes without modification
- ✅ Workflow logs clearly show which tags were published
- ✅ Rollback capability preserved (previous image versions remain on Docker Hub)

### Deployment Validation Workflow
- ✅ Workflow triggers automatically on push/PR to appropriate branches
- ✅ All three services start without errors
- ✅ All health checks pass within timeout
- ✅ Inter-service communication verified (database, Redis)
- ✅ Integration tests pass against running services
- ✅ Docker-compose logs captured for debugging
- ✅ Cleanup removes all containers and volumes
- ✅ Workflow completes in < 5 minutes under normal conditions
- ✅ Clear pass/fail status shown in GitHub Actions UI
- ✅ Logs available in artifacts for failed runs

## Failure Scenarios and Recovery

| Scenario | Workflow | Cause | Recovery |
|----------|----------|-------|----------|
| Tag validation fails | Docker Hub Build | Invalid semver format | Use correct format: `v1.2.3` |
| Docker Hub auth fails | Docker Hub Build | Invalid credentials | Update `DOCKERHUB_TOKEN` secret |
| Build fails | Docker Hub Build | Syntax error in code | Fix code, create new tag |
| Push fails | Docker Hub Build | Network timeout | Retry workflow from GitHub Actions UI |
| Service fails to start | Deployment Validation | Volume permission, port conflict | Check ports free, fix volume permissions |
| Health check timeout | Deployment Validation | Service not responding | Check service logs, verify network |
| Database connection fails | Deployment Validation | PostgreSQL not ready | Increase health check retries/wait time |
| Redis connection fails | Deployment Validation | Redis not ready or network issue | Check Redis service status |

## Related Specifications

- **Detailed Specs** (in `openspec/specs/`):
  - `spec-docker-build-push.md` - Detailed Docker Hub build workflow spec
  - `spec-deployment-validation.md` - Detailed deployment validation workflow spec

- **Archived Change Artifacts** (in `openspec/changes/archive/ci-cd-dockerhub-workflow/`):
  - `proposal.md` - Business justification and impact analysis
  - `design.md` - Technical architecture and component design
  - `tasks.md` - 31 implementation tasks with acceptance criteria
  - `.openspec.yaml` - Change metadata
  - `specs/spec-docker-build-push.md` - Original spec
  - `specs/spec-deployment-validation.md` - Original spec

- **Existing Workflows**:
  - `ci.yml` - CI Pipeline (unit tests, security checks, linting)
  - `cd.yml` - CD Pipeline (production deployment orchestration)
  - `copilot-setup-steps.yml` - GitHub Copilot integration

## Maintenance Notes

### Docker Hub Build Workflow
- Monitor build times and cache hit rates
- Update base image versions quarterly (python, postgres, redis)
- Review and update GitHub Actions action versions monthly
- Track Docker Hub storage usage for image retention

### Deployment Validation Workflow
- Monitor execution time trends
- Review logs for recurring failure patterns
- Update health check timeouts based on observed performance
- Maintain integration test coverage

### Team Operations
- Release process: Tag with semantic version (`git tag v1.2.3 && git push origin v1.2.3`)
- Image access: `docker pull docker.io/DOCKERHUB_USERNAME/rick-morty-api:1.2.3`
- Debugging: Check GitHub Actions artifacts for deployment validation logs
- Emergency rebuild: Use workflow_dispatch in GitHub Actions UI

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-09-14 | Initial archival from change `ci-cd-dockerhub-workflow` |

---

*This specification was promoted from the archived change `ci-cd-dockerhub-workflow` on 2026-09-14. For full implementation history, refer to the archived change artifacts in `openspec/changes/archive/ci-cd-dockerhub-workflow/`.*