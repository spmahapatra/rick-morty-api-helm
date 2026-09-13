# CI/CD Naming Convention for GitHub Actions Workflows

A standardized, self-documenting naming scheme for GitHub Actions workflow files that enables developers to immediately understand a pipeline's purpose, trigger conditions, and execution frequency.

---

## 📋 Executive Summary

The naming convention uses a **structured pattern** that makes workflow files instantly recognizable and discoverable:

```
[category]-[purpose]-[trigger]-[frequency].yml
```

This approach provides:
- ✅ **Immediate clarity** on what each workflow does
- ✅ **Trigger visibility** (when it runs)
- ✅ **Frequency transparency** (how often it runs)
- ✅ **Alphabetical organization** (workflows group logically)
- ✅ **Scalability** (supports complex CI/CD ecosystems)
- ✅ **Discoverability** (easy to find what you need)

---

## 🎯 Naming Pattern

### Core Template

```
[CATEGORY]-[PURPOSE]-[TRIGGER]-[FREQUENCY].yml
```

### Components

| Component | Purpose | Examples | Notes |
|-----------|---------|----------|-------|
| **CATEGORY** | Workflow type | `ci`, `cd`, `security`, `analysis`, `maintenance` | First segment—core function |
| **PURPOSE** | What it does | `test`, `build`, `deploy`, `lint`, `scan`, `release` | Specific action or outcome |
| **TRIGGER** | When it runs | `push`, `pr`, `tag`, `manual`, `scheduled` | Event that activates workflow |
| **FREQUENCY** | How often | `on-demand`, `per-commit`, `nightly`, `weekly`, `hourly` | Execution cadence |

---

## 🏗️ Category Reference

### Primary Categories

| Category | Description | Use Cases |
|----------|-------------|-----------|
| **ci** | Continuous Integration | Tests, linting, type checking, code quality |
| **cd** | Continuous Deployment | Builds, pushes to registries, deployments |
| **security** | Security & Compliance | Scanning, audits, dependency checks, SAST |
| **analysis** | Code & Performance Analysis | Coverage reports, benchmarks, metrics |
| **maintenance** | Maintenance & Operations | Cleanup, cache management, updates |
| **setup** | Configuration & Initialization | Environment setup, secrets management |

---

## 🔔 Trigger Types

| Trigger | GitHub Event | When It Runs | Abbreviation |
|---------|--------------|-------------|--------------|
| **push** | `push` | Every commit to specified branches | `push` |
| **pr** / **pullrequest** | `pull_request` | Pull request opened/updated | `pr` |
| **tag** | `push` with tags | When git tag is pushed | `tag` |
| **manual** / **ondemand** | `workflow_dispatch` | User clicks "Run workflow" | `manual` |
| **scheduled** / **cron** | `schedule` | Cron schedule (time-based) | `scheduled` |
| **multi** | Multiple triggers | Combines multiple conditions | `multi` |
| **release** | `release` event | GitHub release published | `release` |

---

## ⏱️ Frequency Reference

| Frequency | Execution Pattern | Use For |
|-----------|-------------------|---------|
| **on-demand** | Manual trigger only | Setup steps, deployments, rare operations |
| **per-commit** | Every push (multiple times daily) | Fast tests, linting, basic checks |
| **per-pr** | Each PR update | Comprehensive tests, code review prep |
| **nightly** | 1x daily (usually midnight UTC) | Full test suite, heavy builds, scanning |
| **weekly** | 1x weekly (usually Sunday/Monday) | Dependency updates, security audits |
| **hourly** | Every hour | Performance monitoring, scheduled checks |
| **multi-trigger** | Multiple frequencies | Complex workflows with multiple paths |

---

## 📝 Complete Pattern Breakdown

### Basic Formula
```
{category}-{purpose}[-{sub-purpose}]-{trigger}[-{frequency}].yml
```

### Rules

1. **Use hyphens** for word separation (not underscores or camelCase)
2. **Keep it concise** but descriptive (aim for ≤50 characters)
3. **Put category first** for natural sorting
4. **Omit obvious parts** (avoid "github-actions" prefix)
5. **Use consistent terminology** across all workflows
6. **Add sub-purpose** only if needed for clarity
7. **Frequency is optional** if implied by trigger

---

## 📚 Examples by Category

### CI (Continuous Integration) Workflows

```
ci-test-push-per-commit.yml
  ├─ Category: ci (testing/validation)
  ├─ Purpose: test (run test suite)
  ├─ Trigger: push (on every commit)
  └─ Frequency: per-commit (runs after each push)
  └─ When: Every push to main/develop/feature/* branches
  └─ Duration: 5-15 minutes
```

```
ci-lint-pr-per-pr.yml
  ├─ Category: ci (linting/quality)
  ├─ Purpose: lint (code quality checks)
  ├─ Trigger: pr (pull request)
  └─ Frequency: per-pr (on each PR update)
  └─ When: Every PR opened or updated
  └─ Duration: 2-5 minutes
```

```
ci-type-check-push-per-commit.yml
  ├─ Category: ci (type checking)
  ├─ Purpose: type-check (TypeScript validation)
  ├─ Trigger: push
  └─ Frequency: per-commit
  └─ When: Every commit pushed
  └─ Duration: 3-8 minutes
```

```
ci-coverage-report-pr-per-pr.yml
  ├─ Category: ci
  ├─ Purpose: coverage-report (code coverage metrics)
  ├─ Trigger: pr
  └─ Frequency: per-pr
  └─ When: Pull requests
  └─ Duration: 10-20 minutes
```

---

### CD (Continuous Deployment) Workflows

```
cd-build-push-tag-on-demand.yml
  ├─ Category: cd (deployment)
  ├─ Purpose: build-push (build Docker image)
  ├─ Trigger: tag (git tag push)
  └─ Frequency: on-demand (manual, tag-based)
  └─ When: Git tag matching v*.* pushed
  └─ Duration: 10-30 minutes
```

```
cd-docker-hub-registry-tag-on-demand.yml
  ├─ Category: cd
  ├─ Purpose: docker-hub-registry (push to Docker Hub)
  ├─ Trigger: tag
  └─ Frequency: on-demand
  └─ When: Version tags pushed
  └─ Duration: 5-15 minutes
```

```
cd-deploy-staging-manual-on-demand.yml
  ├─ Category: cd
  ├─ Purpose: deploy-staging (staging deployment)
  ├─ Trigger: manual (workflow_dispatch)
  └─ Frequency: on-demand
  └─ When: Manually triggered
  └─ Duration: 15-45 minutes
```

```
cd-deploy-production-manual-on-demand.yml
  ├─ Category: cd
  ├─ Purpose: deploy-production (prod deployment)
  ├─ Trigger: manual
  └─ Frequency: on-demand
  └─ When: Manually triggered (with approvals)
  └─ Duration: 20-60 minutes
```

---

### Security Workflows

```
security-sast-push-nightly.yml
  ├─ Category: security (SAST scanning)
  ├─ Purpose: sast (static analysis)
  ├─ Trigger: push
  └─ Frequency: nightly
  └─ When: Nightly at 2 AM UTC
  └─ Duration: 30-45 minutes
```

```
security-dependencies-scan-scheduled-weekly.yml
  ├─ Category: security
  ├─ Purpose: dependencies-scan (dependency audit)
  ├─ Trigger: scheduled
  └─ Frequency: weekly
  └─ When: Every Monday at 3 AM UTC
  └─ Duration: 10-20 minutes
```

```
security-container-scan-tag-on-demand.yml
  ├─ Category: security
  ├─ Purpose: container-scan (image security scan)
  ├─ Trigger: tag
  └─ Frequency: on-demand
  └─ When: Container images built
  └─ Duration: 5-15 minutes
```

---

### Analysis Workflows

```
analysis-benchmarks-push-nightly.yml
  ├─ Category: analysis
  ├─ Purpose: benchmarks (performance metrics)
  ├─ Trigger: push
  └─ Frequency: nightly
  └─ When: Every night for trending
  └─ Duration: 15-30 minutes
```

```
analysis-coverage-trend-scheduled-weekly.yml
  ├─ Category: analysis
  ├─ Purpose: coverage-trend (coverage metrics)
  ├─ Trigger: scheduled
  └─ Frequency: weekly
  └─ When: Weekly summary
  └─ Duration: 10-15 minutes
```

---

### Maintenance Workflows

```
maintenance-cache-cleanup-scheduled-weekly.yml
  ├─ Category: maintenance
  ├─ Purpose: cache-cleanup (GH action cache)
  ├─ Trigger: scheduled
  └─ Frequency: weekly
  └─ When: Every Saturday at 4 AM UTC
  └─ Duration: 2-5 minutes
```

```
maintenance-dependencies-update-scheduled-weekly.yml
  ├─ Category: maintenance
  ├─ Purpose: dependencies-update (dependency updates)
  ├─ Trigger: scheduled
  └─ Frequency: weekly
  └─ When: Every Monday at 6 AM UTC
  └─ Duration: 15-30 minutes
```

```
maintenance-logs-archive-scheduled-monthly.yml
  ├─ Category: maintenance
  ├─ Purpose: logs-archive (archive old logs)
  ├─ Trigger: scheduled
  └─ Frequency: monthly
  └─ When: 1st of each month
  └─ Duration: 5-10 minutes
```

---

## 🔄 Mapping Current Workflows to New Convention

### Current State → Recommended New Names

| Current Name | Issues | Recommended Name | Reason |
|--------------|--------|------------------|--------|
| `ci.yml` | Too generic | `ci-test-push-per-commit.yml` | Clarifies it's testing, triggered on push, runs per-commit |
| `cd.yml` | Ambiguous | `cd-deploy-manual-on-demand.yml` | Specifies deployment, manual trigger, on-demand |
| `cd-with-dockerhub.yml` | Unclear trigger | `cd-build-push-tag-on-demand.yml` | Clear: builds & pushes on tags, on-demand |
| `fast-track.yml` | Unclear purpose | `ci-validation-pr-per-pr.yml` | States it validates, runs on PRs |
| `fast-track-tag-release.yml` | Vague | `cd-release-validation-tag-on-demand.yml` | Release validation on tag push |
| `copilot-setup-steps.yml` | Not CI/CD specific | `setup-copilot-multi-on-demand.yml` | Setup category, multiple triggers, on-demand |

---

## 📊 Quick Reference Matrix

### Workflow Organization by Trigger & Frequency

```
TRIGGER          ON-DEMAND    PER-COMMIT/PR    NIGHTLY      WEEKLY
─────────────────────────────────────────────────────────────────
push               (X)           ✓                ✓            ✓
  └─ branches                     ✓                
  └─ tags                ✓                        
pull_request              ✓            
schedule                  ✓                       ✓            ✓
manual                    ✓                       ✓            ✓
release                   ✓                       

Legend:
✓ = Recommended usage
(X) = Uncommon but possible
```

### File Naming Decision Tree

```
START: What category is this?
  │
  ├─→ CI (testing/validation)
  │     └─→ Purpose? (test, lint, type-check, coverage)
  │         └─→ Trigger? (push, pr, multi)
  │             └─→ Frequency? (per-commit, per-pr, nightly)
  │
  ├─→ CD (build/deploy)
  │     └─→ Purpose? (build, deploy-staging, deploy-prod)
  │         └─→ Trigger? (tag, manual, release)
  │             └─→ Frequency? (on-demand, nightly)
  │
  ├─→ Security (scanning/audits)
  │     └─→ Purpose? (sast, dast, deps-scan, container-scan)
  │         └─→ Trigger? (push, tag, scheduled)
  │             └─→ Frequency? (nightly, weekly)
  │
  ├─→ Analysis (metrics/reporting)
  │     └─→ Purpose? (benchmarks, coverage, metrics)
  │         └─→ Trigger? (push, scheduled)
  │             └─→ Frequency? (nightly, weekly)
  │
  └─→ Maintenance (operations)
        └─→ Purpose? (cache, deps, logs, cleanup)
            └─→ Trigger? (scheduled, manual)
                └─→ Frequency? (weekly, monthly)
```

---

## 🎓 Naming Examples Gallery

### Simple Examples (Fast Understanding)

| File | Meaning at a Glance |
|------|-------------------|
| `ci-test-push-per-commit.yml` | Run tests on every push |
| `cd-build-push-tag-on-demand.yml` | Build & push when tag is pushed |
| `security-scan-scheduled-weekly.yml` | Security scan every week |

### Descriptive Examples (Full Context)

| File | Purpose | Trigger | Frequency | Estimated Duration |
|------|---------|---------|-----------|-------------------|
| `ci-test-pr-per-pr.yml` | Run all tests | PR update | Per PR | 10-20 min |
| `ci-lint-push-per-commit.yml` | Lint code | Push commit | Per commit | 3-5 min |
| `cd-docker-hub-push-tag-on-demand.yml` | Push to Docker Hub | Git tag | On-demand | 10-15 min |
| `security-sast-push-nightly.yml` | SAST scanning | Scheduled | Nightly | 30-45 min |
| `analysis-benchmarks-scheduled-weekly.yml` | Performance metrics | Scheduled | Weekly | 20-30 min |
| `maintenance-cache-cleanup-scheduled-weekly.yml` | Clean up caches | Scheduled | Weekly | 2-5 min |

---

## 🛠️ Implementation Guide

### Step 1: Categorize All Workflows

List every workflow and assign a category:

```
Current Workflow                  → Category
────────────────────────────────────────────
ci.yml                           → ci
cd.yml                           → cd
cd-with-dockerhub.yml            → cd
fast-track.yml                   → ci
fast-track-tag-release.yml       → cd
copilot-setup-steps.yml          → setup
```

### Step 2: Define Purpose & Trigger

For each workflow, extract the primary purpose and trigger:

```yaml
# Example: ci.yml
name: CI Pipeline
on:
  push:
    branches: [main, develop, feature/*]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

# Analysis:
# - Category: ci (testing/validation)
# - Purpose: test (runs test suite)
# - Triggers: push + pr + manual = multi
# - Frequency: per-commit (every push)
# → New name: ci-test-multi-per-commit.yml
```

### Step 3: Determine Frequency

Map the trigger/schedule to a frequency term:

```
- Every commit to branch = per-commit
- Every PR update = per-pr
- Once per night = nightly
- Once per week = weekly
- Manual only = on-demand
- Multiple patterns = multi-trigger
```

### Step 4: Rename Files

Use Git to safely rename:

```bash
# Using git mv for version control
git mv .github/workflows/ci.yml .github/workflows/ci-test-multi-per-commit.yml
git mv .github/workflows/cd.yml .github/workflows/cd-deploy-manual-on-demand.yml
git mv .github/workflows/cd-with-dockerhub.yml .github/workflows/cd-build-push-tag-on-demand.yml
git mv .github/workflows/fast-track.yml .github/workflows/ci-validation-pr-per-pr.yml
git mv .github/workflows/fast-track-tag-release.yml .github/workflows/cd-release-validation-tag-on-demand.yml

git commit -m "refactor: standardize CI/CD workflow naming convention"
```

### Step 5: Update Documentation

Add a reference table in your repo:

```markdown
# CI/CD Workflows

| Workflow | Purpose | Trigger | Frequency | Duration |
|----------|---------|---------|-----------|----------|
| ci-test-multi-per-commit.yml | Run test suite | push, pr, manual | Per commit | 10-20m |
| cd-deploy-manual-on-demand.yml | Manual deployment | manual | On-demand | 15-45m |
```

---

## ✅ Validation Checklist

When creating or renaming a workflow, verify:

- [ ] **Category is clear** - Immediately recognizable (ci, cd, security, etc.)
- [ ] **Purpose is specific** - Not just "build" but "build-and-test" if needed
- [ ] **Trigger is explicit** - Shows when the workflow runs
- [ ] **Frequency is accurate** - Reflects actual execution cadence
- [ ] **Name is ≤50 characters** - Fits nicely in UI
- [ ] **No ambiguity** - Same workflow name would mean same thing to anyone
- [ ] **Follows hyphen convention** - No underscores or camelCase
- [ ] **Alphabetical grouping** - Workflows naturally group when sorted

---

## 🚀 Advanced Patterns

### For Complex Multi-Purpose Workflows

When a workflow has multiple purposes, use sub-categories:

```
ci-test-lint-type-check-push-per-commit.yml
  └─ Multiple purposes: test + lint + type-check
  
ci-security-sast-dast-push-nightly.yml
  └─ Multiple security scans: sast + dast
```

### For Parameterized Workflows

If using `workflow_dispatch` with inputs, add a suffix:

```
cd-deploy-to-env-manual-on-demand.yml
  └─ Purpose: deploy-to-env (takes environment as input)
  
maintenance-run-task-manual-on-demand.yml
  └─ Purpose: run-task (takes task name as input)
```

### For Matrix Builds

When running multiple configurations, note in purpose:

```
ci-test-matrix-os-push-per-commit.yml
  └─ Purpose: test-matrix-os (tests on multiple OS versions)

ci-build-matrix-versions-push-per-commit.yml
  └─ Purpose: build-matrix-versions (builds against multiple versions)
```

---

## 📋 Glossary of Terms

| Term | Definition | Examples |
|------|-----------|----------|
| **Category** | Top-level workflow type | ci, cd, security, analysis, maintenance |
| **Purpose** | Specific action the workflow performs | test, lint, build, deploy, scan |
| **Trigger** | GitHub event that starts the workflow | push, pull_request, schedule, manual |
| **Frequency** | How often the workflow executes | per-commit, nightly, weekly, on-demand |
| **Multi** | Multiple purposes or triggers combined | multi-trigger, multi-purpose |
| **On-Demand** | Manual execution only (workflow_dispatch) | ci-manual-on-demand |
| **Nightly** | Runs once per day, typically at night | security-scan-nightly |
| **Weekly** | Runs once per week | maintenance-cleanup-weekly |

---

## 🎯 Best Practices

### ✅ DO

- ✅ Use lowercase with hyphens: `ci-test-push-per-commit.yml`
- ✅ Put category first: `ci-*`, `cd-*`, `security-*`
- ✅ Be specific about purpose: `test` not just `ci`
- ✅ Include trigger type: `push`, `pr`, `tag`, `manual`, `scheduled`
- ✅ Specify frequency: `per-commit`, `nightly`, `on-demand`
- ✅ Keep names ≤50 characters
- ✅ Use consistent terminology across all workflows
- ✅ Update this documentation when adding new patterns

### ❌ DON'T

- ❌ Use underscores: `ci_test_push` (use hyphens instead)
- ❌ Use camelCase: `ciTestPush` (use lowercase with hyphens)
- ❌ Make names too generic: `test.yml` (be specific)
- ❌ Omit context: `build.yml` (specify category: `cd-build.yml`)
- ❌ Use abbreviations that aren't standard: `ci-tst` (spell it out)
- ❌ Mix naming styles: One `ci-*.yml`, one `CI-*.yml`
- ❌ Include redundant words: `github-actions-ci` (redundant, use just `ci`)
- ❌ Create super-long names: `continuous-integration-test-on-every-push-to-main-branch` (too long)

---

## 📊 Current Project Mapping

### Before Standardization

```
.github/workflows/
├── cd-with-dockerhub.yml          ❌ Trigger unclear
├── cd.yml                          ❌ Too generic
├── ci.yml                          ❌ Too generic
├── copilot-setup-steps.yml         ❌ Not CI/CD specific
├── fast-track-tag-release.yml      ❌ Purpose vague
└── fast-track.yml                  ❌ Multiple issues
```

### After Standardization (Recommended)

```
.github/workflows/
├── ci-test-multi-per-commit.yml                    ✅ Replaces: ci.yml
├── ci-validation-pr-per-pr.yml                     ✅ Replaces: fast-track.yml
├── cd-deploy-manual-on-demand.yml                  ✅ Replaces: cd.yml
├── cd-build-push-tag-on-demand.yml                 ✅ Replaces: cd-with-dockerhub.yml
├── cd-release-validation-tag-on-demand.yml         ✅ Replaces: fast-track-tag-release.yml
└── setup-copilot-multi-on-demand.yml               ✅ Replaces: copilot-setup-steps.yml
```

---

## 🔗 Integration with Repository Documentation

Add this section to your project's README or CI/CD guide:

```markdown
## Workflow Naming Convention

All workflows follow a standardized naming pattern for clarity:

**Pattern:** `[category]-[purpose]-[trigger]-[frequency].yml`

### Quick Reference

| File | Triggers | Frequency |
|------|----------|-----------|
| `ci-test-multi-per-commit.yml` | push, PR, manual | Per commit |
| `cd-build-push-tag-on-demand.yml` | git tag push | On-demand |
| `security-scan-scheduled-weekly.yml` | cron schedule | Weekly |

See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) for complete details.
```

---

## 📞 FAQ

**Q: Should I include test suite name in the workflow name?**  
A: Only if you have multiple test workflows. Example: `ci-test-unit-push-per-commit.yml` vs `ci-test-integration-scheduled-nightly.yml`

**Q: What if a workflow has multiple triggers with different frequencies?**  
A: Use `multi-trigger` for the trigger and describe in the workflow name: `ci-test-multi-trigger-per-commit.yml` (though it's better to split into separate workflows)

**Q: Should deprecated workflows be renamed?**  
A: Yes, rename with a `deprecated-` prefix and mark for removal: `deprecated-ci-old-linter-push-per-commit.yml`

**Q: Can I use the old names for backwards compatibility?**  
A: GitHub Actions allows symlinks or keeping old names. Prefer full rename + git history over compatibility names.

**Q: Should branch names appear in the workflow filename?**  
A: No, the workflow YAML contains branch info. The filename shouldn't repeat it.

---

## 🎓 Summary

This standardized naming convention provides:

1. **Instant Recognition** - Developers immediately understand what each workflow does
2. **Efficient Discovery** - Alphabetical sorting groups related workflows
3. **Clear Triggers** - File name shows when the workflow runs
4. **Frequency Transparency** - Execution cadence is immediately obvious
5. **Scalability** - Works for 6 workflows or 60+ workflows
6. **Maintenance** - Easier to find and update workflows
7. **Documentation** - File names serve as self-documentation
8. **Onboarding** - New team members quickly understand the CI/CD structure

Use this convention consistently across your organization for maximum benefit!

---

## 📄 Document Information

- **Version:** 1.0
- **Created:** 2026-09-14
- **Repository:** setupAppCreDepHelmPkg
- **Author:** CI/CD Infrastructure Team
- **Status:** Recommended for adoption
