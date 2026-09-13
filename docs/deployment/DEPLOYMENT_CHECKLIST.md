# Deployment Checklist

Complete this checklist before deploying to production.

## Pre-Deployment (1-2 days before)

### Code Quality
- [ ] All tests passing: `pytest --cov=src`
- [ ] Code coverage ≥ 80%: `pytest --cov=src --cov-report=term`
- [ ] No linting errors: `flake8 src/`
- [ ] No type errors: `mypy src/`
- [ ] Code formatted: `black src/`
- [ ] Security scan passed: `bandit -r src/`
- [ ] All TODO/FIXME comments addressed or documented

### Documentation
- [ ] README.md updated with current version
- [ ] API documentation current: `docs/api/API_REFERENCE.md`
- [ ] Architecture documented: `docs/architecture/ARCHITECTURE_OVERVIEW.md`
- [ ] Deployment guide reviewed: `docs/deployment/PRODUCTION_RUNBOOK.md`
- [ ] CHANGELOG.md updated with release notes
- [ ] Known issues documented

### Dependencies
- [ ] `requirements.txt` pinned to specific versions
- [ ] No security vulnerabilities: `safety check`
- [ ] All critical dependencies reviewed
- [ ] Version compatibility verified (Python 3.9+)

### Configuration
- [ ] All environment variables documented
- [ ] Production configuration reviewed
- [ ] No hardcoded secrets or credentials
- [ ] Database connection strings correct
- [ ] Cache TTL values appropriate
- [ ] Log levels set correctly (INFO or above)

## 24 Hours Before Deployment

### Testing
- [ ] Full test suite runs without errors
- [ ] Integration tests pass
- [ ] Performance tests baseline established
- [ ] Load testing completed (if applicable)
- [ ] Stress testing passed

### Database
- [ ] Schema changes reviewed and tested
- [ ] Migration scripts tested on staging
- [ ] Backup strategy verified
- [ ] Rollback procedure documented
- [ ] Database credentials secured in secret manager

### Infrastructure
- [ ] Docker images built successfully
- [ ] Docker image scanned for vulnerabilities
- [ ] Docker Compose file validated
- [ ] Kubernetes manifests validated (if applicable)
- [ ] Load balancer configuration reviewed
- [ ] DNS records prepared (if needed)

### Team Coordination
- [ ] Deployment window scheduled
- [ ] Team members notified
- [ ] Stakeholders informed
- [ ] Rollback plan communicated
- [ ] On-call engineer assigned

## Deployment Day

### Pre-Deployment Sync
- [ ] Latest code merged to main branch
- [ ] All checks passing in CI/CD
- [ ] Staging environment healthy
- [ ] Database backups complete
- [ ] Team ready (everyone online/available)

### Deployment Execution
- [ ] Pull latest code: `git pull origin main`
- [ ] Build Docker image: `docker build -t api:v1.0.0 .`
- [ ] Push to registry: `docker push registry/api:v1.0.0`
- [ ] Health checks passing
- [ ] Database migrations applied (if needed)
- [ ] Cache cleared: `POST /cache/flush`
- [ ] Start new containers
- [ ] Monitor logs for errors

### Post-Deployment Validation (15 minutes)
- [ ] Health endpoint responding: `curl /health`
- [ ] API endpoints working: `curl /characters/1`
- [ ] Cache functioning: `curl /cache/stats`
- [ ] Database queries successful
- [ ] No critical errors in logs
- [ ] Performance metrics normal
- [ ] Error rates acceptable
- [ ] External API connectivity OK

## Post-Deployment (First Hour)

### Monitoring
- [ ] Error logs reviewed for issues
- [ ] Performance metrics reviewed
- [ ] CPU/Memory usage normal
- [ ] Database connections healthy
- [ ] Cache hit rate acceptable (>50%)
- [ ] Response times consistent
- [ ] No unusual error patterns

### Testing
- [ ] Smoke tests passed: `pytest tests/test_smoke.py`
- [ ] User-facing features verified
- [ ] Critical workflows tested
- [ ] API response formats correct
- [ ] Data consistency verified

### Communication
- [ ] Team notified deployment successful
- [ ] Stakeholders informed
- [ ] Deployment recorded in log
- [ ] Known issues documented (if any)

## Post-Deployment (Next 24 Hours)

### Monitoring
- [ ] Continue monitoring logs
- [ ] Watch for delayed failure patterns
- [ ] Performance metrics stable
- [ ] Error rates normal
- [ ] No unusual resource usage

### User Validation
- [ ] No user-reported issues
- [ ] Feature behavior as expected
- [ ] Data integrity confirmed
- [ ] Integration with other systems OK

### Documentation
- [ ] Deployment documented
- [ ] Any issues recorded
- [ ] Performance baseline updated
- [ ] Lessons learned captured

## Rollback Criteria

Consider rollback if:
- [ ] Critical service unavailable (>5 min)
- [ ] Data corruption detected
- [ ] Response times increased >50%
- [ ] Error rate >5% (vs. baseline)
- [ ] Cascading failures to dependent systems
- [ ] Database connectivity lost
- [ ] Cache unavailable

### Rollback Procedure
1. Stop new containers: `docker-compose down`
2. Revert database migrations (if needed)
3. Start previous version containers
4. Verify health checks passing
5. Notify team and stakeholders
6. Investigate root cause
7. Document incident

## Rollback Execution

If rollback needed:
- [ ] Execute rollback procedure above
- [ ] Verify system stable
- [ ] Alert all stakeholders
- [ ] Document what went wrong
- [ ] Schedule post-mortem within 48 hours
- [ ] Do NOT rush to re-deploy without fixes

## Version Management

### Before Release
- [ ] Version number incremented (semver)
- [ ] Git tag created: `git tag -a v1.0.0 -m "Release 1.0.0"`
- [ ] Tag pushed: `git push origin v1.0.0`
- [ ] Release notes published
- [ ] Changelog updated

### Docker Images
- [ ] Image tagged with version: `api:v1.0.0`
- [ ] Image tagged as latest: `api:latest`
- [ ] Both tags pushed to registry

## Production Handoff

- [ ] Monitoring configured
- [ ] On-call procedures documented
- [ ] Emergency contacts shared
- [ ] Runbook reviewed with team
- [ ] Log access provided
- [ ] Dashboard access provided
- [ ] Alert thresholds configured
- [ ] Escalation procedures clear

## Related Documentation

- Full runbook: `docs/deployment/PRODUCTION_RUNBOOK.md`
- Troubleshooting: `docs/deployment/TROUBLESHOOTING_GUIDE.md`
- Monitoring: `docs/operations/MONITORING_GUIDE.md`
- Health checks: `docs/operations/HEALTH_CHECKS.md`

## Questions?

See `docs/deployment/` for detailed procedures and `docs/operations/` for operational guidance.
