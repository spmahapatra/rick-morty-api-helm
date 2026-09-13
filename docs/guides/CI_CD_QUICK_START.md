# CI/CD Pipeline Implementation Checklist
## setupAppCreDepHelmPkg - Quick Start Guide

**Objective**: Set up automated CI/CD with tag-triggered fast validation and Docker Hub image push  
**Estimated Time**: 30-45 minutes for initial setup  
**Effort Level**: Low (mostly copy-paste and configuration)

---

## Phase 1: Docker Hub Setup (10 minutes)

### [ ] 1.1 Create Docker Hub Token
- [ ] Go to https://hub.docker.com/settings/security
- [ ] Click "New Access Token"
- [ ] Name: `github-actions-token`
- [ ] Copy token value (save somewhere safe)

### [ ] 1.2 Add GitHub Secrets
- [ ] Go to repo Settings → Secrets and variables → Actions
- [ ] Click "New repository secret"
- [ ] Secret 1: Name=`DOCKERHUB_USERNAME`, Value=your Docker Hub username
- [ ] Secret 2: Name=`DOCKERHUB_TOKEN`, Value=token from 1.1
- [ ] Verify both secrets appear as bullet points

---

## Phase 2: Deploy Fast Track Workflow (5 minutes)

### [ ] 2.1 Verify Workflow File
```bash
ls -la .github/workflows/fast-track-tag-release.yml
```
- [ ] File exists and shows recent timestamp

### [ ] 2.2 Commit and Push
```bash
git add .github/workflows/fast-track-tag-release.yml
git commit -m "feat: add fast-track tag release validation workflow"
git push origin main
```
- [ ] Push completes without errors

### [ ] 2.3 Test with Tag
```bash
git tag v0.1.0-test
git push origin v0.1.0-test
```
- [ ] Go to Actions tab: https://github.com/YOUR_USER/setupAppCreDepHelmPkg/actions
- [ ] See "Fast Track Release Validation" workflow running
- [ ] Workflow completes in 4-5 minutes
- [ ] Cleanup test tag: `git push origin --delete v0.1.0-test` and `git tag -d v0.1.0-test`

---

## Phase 3: Deploy Docker Hub Push Workflow (10 minutes)

### [ ] 3.1 Customize Docker Hub Image Name
- [ ] Open: `.github/workflows/cd-with-dockerhub.yml`
- [ ] Find line: `DOCKERHUB_IMAGE_NAME: yourname/rick-morty-api`
- [ ] Replace `yourname` with your Docker Hub username
- [ ] Save file

### [ ] 3.2 Copy to Active Workflows
```bash
cp cd-with-dockerhub.yml .github/workflows/cd-docker-push.yml
```
- [ ] File copied successfully

### [ ] 3.3 Commit and Push
```bash
git add .github/workflows/cd-docker-push.yml
git commit -m "feat: add docker hub image push workflow"
git push origin main
```
- [ ] Push completes without errors

### [ ] 3.4 Test Push Workflow
```bash
git tag v0.2.0-test
git push origin v0.2.0-test
```
- [ ] Go to Actions tab
- [ ] Fast Track runs first (4-5 min)
- [ ] CD Pipeline runs after (5-10 min)
- [ ] Check Docker Hub: https://hub.docker.com/repository/docker/yourname/rick-morty-api
- [ ] Verify image tag `v0.2.0-test` appears
- [ ] Cleanup: `git push origin --delete v0.2.0-test` and `git tag -d v0.2.0-test`

---

## Phase 4: Deploy Deployment Validation (10 minutes)

### [ ] 4.1 Create Deploy Validation Workflow
- [ ] Copy the workflow YAML from `CI_CD_IMPLEMENTATION_GUIDE.md` (Section 4)
- [ ] Create file: `.github/workflows/deploy-validation.yml`
- [ ] Paste the content
- [ ] Save file

### [ ] 4.2 Commit and Push
```bash
git add .github/workflows/deploy-validation.yml
git commit -m "feat: add deployment validation workflow"
git push origin main
```
- [ ] Push completes without errors

### [ ] 4.3 Test Validation Workflow
```bash
git commit --allow-empty -m "test: trigger deployment validation"
git push origin main
```
- [ ] Go to Actions tab
- [ ] See "Deployment Validation" workflow running
- [ ] Workflow completes successfully
- [ ] All services (postgres, redis, app) are healthy

---

## Phase 5: Verification & Documentation (5 minutes)

### [ ] 5.1 Verify All Workflows Active
- [ ] Go to: Actions tab of your GitHub repo
- [ ] Confirm three workflows exist:
  - [ ] `Fast Track Release Validation` (runs on tags)
  - [ ] `CD Pipeline` (cd-docker-push.yml)
  - [ ] `Deployment Validation` (runs on push/PR)

### [ ] 5.2 Check Workflow Status
- [ ] Click each workflow
- [ ] Confirm last run status
- [ ] All should show recent successful runs

### [ ] 5.3 Document Your Setup
- [ ] Update team documentation with:
  - [ ] How to create releases: `git tag v1.2.3`
  - [ ] Where to monitor: GitHub Actions tab
  - [ ] Where to find images: Docker Hub + GHCR
  - [ ] Troubleshooting: See CI_CD_IMPLEMENTATION_GUIDE.md

---

## Daily Usage

### Creating a Release
```bash
# 1. Ensure all changes are committed and pushed
git status

# 2. Create semantic version tag
git tag v1.2.3

# 3. Push tag (triggers Fast Track → CD Pipeline)
git push origin v1.2.3

# 4. Monitor workflows
# Go to: https://github.com/YOUR_USER/setupAppCreDepHelmPkg/actions
# Watch progress in real-time
```

### Expected Workflow Sequence on Tag
1. **Fast Track** (4-5 min): Validates build + docker-compose
2. **CD Pipeline** (5-10 min): Builds multi-platform image + pushes to Docker Hub + GHCR
3. **Status Check** (1 min): Reports overall results

**Total Time**: ~15 minutes from tag to image ready on Docker Hub

### Accessing Published Images
```bash
# Pull from Docker Hub
docker pull yourname/rick-morty-api:v1.2.3
docker pull yourname/rick-morty-api:latest

# Pull from GitHub Container Registry
docker pull ghcr.io/YOUR_USER/setupAppCreDepHelmPkg:v1.2.3

# Use in docker-compose.yml
services:
  app:
    image: yourname/rick-morty-api:v1.2.3
```

---

## Monitoring & Maintenance

### Weekly
- [ ] Review workflow execution times
- [ ] Check for any failed runs
- [ ] Investigate and fix failures

### Monthly
- [ ] Clean up old Docker images on Docker Hub
- [ ] Review and rotate secrets if needed
- [ ] Check for workflow updates

### Quarterly
- [ ] Performance optimization review
- [ ] Update base images (python, postgres, redis)
- [ ] Security audit of workflows

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| **Tag doesn't trigger Fast Track** | Ensure tag matches `v*` pattern (e.g., `v1.2.3`) |
| **Docker Hub push fails** | Check DOCKERHUB_TOKEN secret exists and has correct permissions |
| **Deployment validation hangs** | App health endpoint may be slow; check `.github/workflows/deploy-validation.yml` timeout values |
| **Workflow not visible** | Refresh browser or check Actions tab filters |
| **Service health checks fail** | Test locally: `docker-compose up -d` then `docker-compose logs` |

---

## Cost Verification

After implementation, verify you're within free tier:

```
Monthly GitHub Actions minutes:
- Fast Track per tag: 4-5 minutes
- CD Pipeline per release: 5-10 minutes
- Deployment Validation per push: 2-3 minutes

Example (2 releases/month, 10 pushes/month):
- 2 × 15 min (releases) = 30 min
- 10 × 2.5 min (deployments) = 25 min
- Total: ~55 min/month ✅ (well under 2,000 min free tier)

Cost: $0/month
```

---

## Sign-Off

- [ ] All workflows deployed and tested
- [ ] Docker Hub images accessible
- [ ] Team trained on release process
- [ ] Documentation updated
- [ ] Ready for production use

---

## Quick Links

- GitHub Actions Dashboard: https://github.com/YOUR_USER/setupAppCreDepHelmPkg/actions
- Docker Hub Images: https://hub.docker.com/repository/docker/yourname/rick-morty-api
- Docker Hub Tokens: https://hub.docker.com/settings/security
- GitHub Secrets: https://github.com/YOUR_USER/setupAppCreDepHelmPkg/settings/secrets/actions
- Implementation Guide: `CI_CD_IMPLEMENTATION_GUIDE.md`

---

**Status: Ready to Implement** ✅

All files are prepared and ready for deployment. Follow the checklist above to complete setup in approximately 45 minutes.

For detailed information, refer to `CI_CD_IMPLEMENTATION_GUIDE.md`.
