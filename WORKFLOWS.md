# GitHub Actions Workflows

This project uses standardized workflow naming: `[category]-[purpose]-[trigger]-[frequency].yml`

## Active Workflows

| Workflow | Category | Purpose | Triggers | Frequency | Duration | Status |
|----------|----------|---------|----------|-----------|----------|--------|
| `cd-build-push-tag-on-demand.yml` | CD | Build & push Docker images to GHCR + Docker Hub | git tag push | On-demand | 10-30m | ✅ Active |
| `cd-deploy-manual-on-demand.yml` | CD | Manual deployments to staging/prod | workflow_dispatch | On-demand | 20-60m | ✅ Active |
| `cd-release-validation-tag-on-demand.yml` | CD | Release validation (syntax, tests, docker-compose) | git tag push | On-demand | 10-15m | ✅ Active |
| `ci-test-multi-per-commit.yml` | CI | Run comprehensive test suite | push, PR, manual | Per commit | 10-20m | ✅ Active |
| `ci-validation-pr-per-pr.yml` | CI | Quick validation (lint, type-check) | PR, push, manual | Per PR | 5-10m | ✅ Active |
| `setup-copilot-multi-on-demand.yml` | Setup | Copilot environment setup | push, PR, manual | Per commit | 2-5m | ✅ Active |

## Naming Convention

All workflows follow a standardized naming pattern for clarity and discoverability.

**Pattern:** `[category]-[purpose]-[trigger]-[frequency].yml`

### Categories
- **ci** - Continuous Integration (tests, linting, type-checking)
- **cd** - Continuous Deployment (builds, pushes, deployments)
- **security** - Security & Compliance (scanning, audits)
- **analysis** - Code Analysis (metrics, benchmarks)
- **maintenance** - Operations (cleanup, updates)
- **setup** - Configuration & setup

### Triggers
- **push** - Every git push to branches
- **pr** - Pull request opened/updated
- **tag** - Git tag push (releases)
- **manual** - User clicks "Run workflow" button (workflow_dispatch)
- **scheduled** - Cron schedule (time-based)
- **multi** - Multiple trigger types

### Frequencies
- **per-commit** - Every git push (multiple times daily)
- **per-pr** - Each pull request update
- **hourly** - Every hour
- **nightly** - Once per night
- **weekly** - Once per week
- **monthly** - Once per month
- **on-demand** - Manual trigger only

## Workflow Triggers by Event

### On Git Push (push)
- `ci-test-multi-per-commit.yml` - Runs test suite
- `ci-validation-pr-per-pr.yml` - Runs quick validation
- `setup-copilot-multi-on-demand.yml` - Copilot setup

### On Pull Request (pull_request)
- `ci-test-multi-per-commit.yml` - Runs test suite
- `ci-validation-pr-per-pr.yml` - Runs quick validation
- `setup-copilot-multi-on-demand.yml` - Copilot setup

### On Git Tag Push (push with tags)
- `cd-build-push-tag-on-demand.yml` - Builds & pushes Docker images
- `cd-release-validation-tag-on-demand.yml` - Validates release

### Manual Trigger (workflow_dispatch)
- `cd-deploy-manual-on-demand.yml` - Performs deployment
- All workflows support manual trigger via "Run workflow" button

## Testing Workflows Locally

### Test CI Workflows (Push/PR)
```bash
# Create test commit to trigger CI workflows
git commit --allow-empty -m "test: trigger CI workflows"
git push origin <your-branch>

# Monitor GitHub Actions tab
# Expected: ci-test-multi-per-commit.yml and ci-validation-pr-per-pr.yml start
```

### Test CD Workflows (Tag-Triggered)
```bash
# Create test tag to trigger CD workflows
git tag v0.1.0-test
git push origin v0.1.0-test

# Monitor GitHub Actions tab
# Expected: cd-build-push-tag-on-demand.yml and cd-release-validation-tag-on-demand.yml start

# Cleanup test tag
git tag -d v0.1.0-test
git push origin --delete v0.1.0-test
```

### Test Manual Workflows
1. Go to GitHub → Actions tab
2. Select a workflow from the list
3. Click "Run workflow" button
4. Select branch and click "Run workflow"

## Adding New Workflows

When creating new workflows, follow the naming convention:

1. **Determine category** - ci, cd, security, analysis, maintenance, setup
2. **Define purpose** - What the workflow does (test, build, deploy, scan, etc.)
3. **Identify trigger** - When it runs (push, pr, tag, manual, scheduled, multi)
4. **Specify frequency** - How often (per-commit, nightly, weekly, on-demand, etc.)
5. **Create filename** - `[category]-[purpose]-[trigger]-[frequency].yml`
6. **Update this file** - Add to WORKFLOWS.md

### Example Template
```yaml
name: My Workflow
# Filename: [category]-[purpose]-[trigger]-[frequency].yml
# Category: (ci|cd|security|analysis|maintenance|setup)
# Purpose: (what this workflow does)
# Triggers: (when this runs)
# Frequency: (how often)
# Duration: (estimated runtime)

on:
  push:
    branches: [main, develop]
  # Add other triggers as needed

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      # Your workflow steps
```

## Documentation

For complete details on the naming convention and implementation:

- **[CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md)** - Comprehensive reference guide
- **[WORKFLOW_NAMING_QUICK_REFERENCE.md](./WORKFLOW_NAMING_QUICK_REFERENCE.md)** - Quick lookup cheat sheet
- **[NAMING_CONVENTION_VISUAL_GUIDE.txt](./NAMING_CONVENTION_VISUAL_GUIDE.txt)** - Visual examples with ASCII art
- **[WORKFLOW_RENAMING_GUIDE.md](./WORKFLOW_RENAMING_GUIDE.md)** - Implementation details
- **[IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)** - Step-by-step checklist

## Workflow Metadata

| Workflow | Last Updated | Status | Maintainer |
|----------|---|---|---|
| cd-build-push-tag-on-demand.yml | 2026-09-14 | ✅ Active | CI/CD Team |
| cd-deploy-manual-on-demand.yml | 2026-09-14 | ✅ Active | CI/CD Team |
| cd-release-validation-tag-on-demand.yml | 2026-09-14 | ✅ Active | CI/CD Team |
| ci-test-multi-per-commit.yml | 2026-09-14 | ✅ Active | CI/CD Team |
| ci-validation-pr-per-pr.yml | 2026-09-14 | ✅ Active | CI/CD Team |
| setup-copilot-multi-on-demand.yml | 2026-09-14 | ✅ Active | CI/CD Team |

---

**Naming Convention Version:** 1.0  
**Last Updated:** 2026-09-14  
**Repository:** setupAppCreDepHelmPkg
