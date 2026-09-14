# OpenSpec Capability Inventory

**Last Updated:** 2026-09-14  
**Status:** Active Capability Registry  

This document tracks all archived changes and their promoted capability specifications.

---

## Archived Capabilities

### 1. API Resilience & Observability Enhancement

**Change ID:** `api-resilience-enhancement`  
**Archive Date:** 2026-09-13  
**Status:** ✅ Formalized & Archived  
**Priority:** High  

**Capability Summary:**
Transform the Rick and Morty API wrapper from a basic Flask application into a production-ready, resilient service with enterprise-grade caching, data persistence, observability, and Kubernetes orchestration.

**Key Capabilities:**
- High-Performance Caching (Redis, 80%+ hit ratio)
- Data Persistence (PostgreSQL with audit trails)
- Resilience Patterns (exponential backoff, circuit breaker, graceful degradation)
- Enterprise Observability (structured JSON logging, health checks, Kubernetes probes)
- Traffic Control (token bucket rate limiting with per-consumer tiers)
- Production Deployment (Docker Compose & Helm charts)

**Durable Specification:**
- **Main Spec:** `api-resilience-enhancement-spec.md` (consolidated capability specification)
- **Detailed Specs:**
  - `01-caching.md` - Redis caching layer with TTL and invalidation
  - `02-persistence.md` - PostgreSQL schema and data sync
  - `03-resilience-ratelimit.md` - Retry logic, circuit breaker, rate limiting
  - `04-observability.md` - Structured logging, health checks, Kubernetes probes

**Performance Targets:**
- Cache hit ratio: ≥ 80%
- Cached request latency: < 100ms (p99)
- 99.5% uptime
- All requests logged as JSON Lines
- Rate limiting enforces quotas with 99% accuracy

**Archive Location:**
`openspec/changes/archive/api-resilience-enhancement/`

**Archived Artifacts:**
- Proposal: Business justification and impact analysis
- Design: Technical architecture and component design
- Tasks: 39 implementation tasks with acceptance criteria
- Change Metadata: `.openspec.yaml` with project details

**Technology Stack:**
- Application: Flask 3.0+, Gunicorn 21+
- Caching: Redis 7.0+
- Persistence: PostgreSQL 13+, SQLAlchemy 2.0+, Alembic 1.12+
- Resilience: tenacity 8.2+, PyBreaker
- Observability: python-json-logger 2.0+, prometheus-client 0.17+
- DevOps: Docker 24+, Kubernetes 1.27+, Helm 3.12+

**Deployment Options:**
1. Local Development: Docker Compose with full stack
2. Production: Kubernetes with Helm charts (Minikube for testing)
3. CI/CD: GitHub Actions automated testing and deployment

**Maintenance Notes:**
- Refer to `api-resilience-enhancement-spec.md` for configuration and operations
- All implementation tasks documented in archived change
- Health checks monitor Redis, PostgreSQL, and upstream API
- Log shipping via Filebeat to ELK/OpenSearch stack
- Metrics available via Prometheus endpoint

---

### 2. Rick & Morty API Initial Spec (Previously Archived)

**Change ID:** `rick-morty-api-initial-spec`  
**Archive Date:** Earlier (prior to current session)  
**Status:** ✅ Archived  
**Priority:** Medium

**Capability Summary:**
Initial specification of the Rick and Morty API wrapper Flask application.

**Archive Location:**
`openspec/changes/archive/rick-morty-api-initial-spec/`

**Durable Specification:**
`openspec/specs/rick-morty-api/spec.md` (if available)

---

### 3. CI/CD Docker Hub and Deployment Validation Workflows

**Change ID:** `ci-cd-dockerhub-workflow`  
**Archive Date:** 2026-09-14  
**Status:** ✅ Formalized & Archived  
**Priority:** High

**Capability Summary:**
Implement automated Docker image build/push on git tags and deployment validation workflows with Docker Compose to ensure reliable container deployments to Docker Hub and Kubernetes.

**Key Capabilities:**
- Automated Image Build and Push to Docker Hub on semantic version tags
- Multi-platform Docker image builds (linux/amd64, linux/arm64)
- Docker Hub layer caching for faster builds
- Deployment validation of complete docker-compose stack (PostgreSQL, Redis, API)
- Health check verification for all services
- Inter-service communication validation
- Integration test execution against running stack
- Diagnostic log collection and artifact upload

**Durable Specification:**
- **Main Spec:** `ci-cd-dockerhub-workflow-spec.md` (consolidated capability specification)
- **Detailed Specs:**
  - `spec-docker-build-push.md` - Docker Hub image build and push workflow
  - `spec-deployment-validation.md` - Deployment validation workflow

**Performance Targets:**
- Image build time: < 10 minutes
- Deployment validation: < 5 minutes (target), < 15 minutes (max)
- Service startup: < 60 seconds for all services
- Health checks: 120 seconds max wait time

**Archive Location:**
`openspec/changes/archive/ci-cd-dockerhub-workflow/`

**Archived Artifacts:**
- Proposal: Business justification and impact analysis
- Design: Technical architecture and component design
- Tasks: 31 implementation tasks with acceptance criteria
- Change Metadata: `.openspec.yaml` with project details

**Technology Stack:**
- CI/CD Platform: GitHub Actions
- Container Registry: Docker Hub (docker.io)
- Container Runtime: Docker, docker-compose
- Base Images: python:3.9-slim, postgres:15-alpine, redis:7-alpine
- Build Tools: Docker Buildx, docker/build-push-action@v4
- Registry Auth: Docker Hub Personal Access Tokens

**Deployment Options:**
1. Local Development: Docker Compose with local build
2. Team Collaboration: Docker Compose with pre-built Docker Hub images
3. Production: Kubernetes with Helm charts using Docker Hub images

**Maintenance Notes:**
- Refer to `ci-cd-dockerhub-workflow-spec.md` for configuration and operations
- All implementation tasks documented in archived change
- Release process: Tag with semantic version (`git tag v1.2.3 && git push origin v1.2.3`)
- Image access: `docker pull docker.io/DOCKERHUB_USERNAME/rick-morty-api:1.2.3`
- Debugging: Check GitHub Actions artifacts for deployment validation logs
- Emergency rebuild: Use workflow_dispatch in GitHub Actions UI

---

## Spec Files Organization

### Main Capability Specs

```
openspec/specs/
├── .gitkeep
├── api-resilience-enhancement-spec.md    ← Consolidated durable spec
├── 01-caching.md                          ← Detailed caching spec
├── 02-persistence.md                      ← Detailed persistence spec
├── 03-resilience-ratelimit.md             ← Detailed resilience spec
├── 04-observability.md                    ← Detailed observability spec
├── ci-cd-dockerhub-workflow-spec.md       ← CI/CD workflows consolidated spec
├── spec-docker-build-push.md              ← Docker Hub build workflow spec
├── spec-deployment-validation.md          ← Deployment validation workflow spec
└── rick-morty-api/
    └── spec.md                             ← Initial API spec (if available)
```

### Change Archives

```
openspec/changes/archive/
├── api-resilience-enhancement/
│   ├── .openspec.yaml                    ← Change metadata
│   ├── proposal.md                       ← Business justification
│   ├── design.md                         ← Technical design
│   ├── tasks.md                          ← Implementation tasks (39 total)
│   └── specs/                            ← Original spec files
│       ├── 01-caching.md
│       ├── 02-persistence.md
│       ├── 03-resilience-ratelimit.md
│       └── 04-observability.md
├── ci-cd-dockerhub-workflow/
│   ├── .openspec.yaml                    ← Change metadata
│   ├── proposal.md                       ← Business justification
│   ├── design.md                         ← Technical design
│   ├── tasks.md                          ← Implementation tasks (31 total)
│   └── specs/                            ← Original spec files
│       ├── spec-docker-build-push.md
│       └── spec-deployment-validation.md
└── rick-morty-api-initial-spec/
    ├── design.md
    ├── proposal.md
    ├── tasks.md
    └── specs/
        └── rick-morty-api/spec.md
```

---

## Archival Process Checklist

For each change archived to this inventory, the following steps are completed:

- ✅ Move change artifacts to `openspec/changes/archive/{change-id}/`
- ✅ Copy specification files to `openspec/specs/`
- ✅ Create consolidated durable spec.md file
- ✅ Document in capability inventory (this file)
- ✅ Update all references in project documentation
- ✅ Validate all health checks and monitoring
- ✅ Sign off on completion

---

## How to Use This Inventory

### For Implementation Teams
1. Refer to the durable capability spec (e.g., `api-resilience-enhancement-spec.md`)
2. Check detailed specs for specific layer information
3. Review archived change for full history and original tasks
4. Use configuration reference for environment setup

### For Operations Teams
1. Monitor health checks as defined in capability spec
2. Set up alerting based on performance targets
3. Refer to operations runbooks in durable spec
4. Track metrics via Prometheus endpoint
5. Aggregate logs via Filebeat + ELK/OpenSearch

### For Project Planning
1. Review all archived capabilities for existing features
2. Avoid duplicating already-formalized capabilities
3. Check for integration points with existing capabilities
4. Plan new changes building on top of established capabilities

---

## Future Changes

When archiving new changes to OpenSpec:

1. **Before Archival:**
   - Validate all implementation tasks are complete
   - Verify all acceptance criteria met
   - Confirm health checks passing
   - Update project documentation

2. **During Archival:**
   - Move change artifacts to archive directory
   - Promote specs to main specs directory
   - Create consolidated durable spec.md
   - Update this capability inventory

3. **After Archival:**
   - Communicate to team
   - Update any external documentation
   - Set up ongoing monitoring and maintenance
   - Schedule regular review cycles

---

## Capability Lifecycle

```
Proposed → Specified → Implementing → Complete → Archived → Maintained

api-resilience-enhancement:  ✅ Complete → ✅ Archived (2026-09-13)
ci-cd-dockerhub-workflow:    ✅ Complete → ✅ Archived (2026-09-14)
```

Once a capability is archived and formalized, it enters the maintenance phase where:
- Configuration can be adjusted based on operational needs
- Performance targets are monitored
- Issues are resolved based on documented runbooks
- Future enhancements are tracked as separate changes

---

## References

- **OpenSpec Config:** `openspec/config.yaml`
- **Project README:** Root `README.md`
- **Operations Runbooks:** Embedded in each durable spec.md
- **Archived Changes:** `openspec/changes/archive/`
