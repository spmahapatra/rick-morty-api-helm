# Workflow Naming Convention - Quick Reference Card

A one-page reference for the standardized CI/CD workflow naming convention.

---

## 🎯 The Pattern

```
[CATEGORY]-[PURPOSE]-[TRIGGER]-[FREQUENCY].yml
```

**Example:** `ci-test-push-per-commit.yml`

---

## 📋 Component Reference

### Categories (Pick One)
| Category | Use For |
|----------|---------|
| `ci` | Testing, linting, type-checking, validation |
| `cd` | Building, pushing images, deploying |
| `security` | Scanning, audits, compliance checks |
| `analysis` | Metrics, benchmarks, coverage reports |
| `maintenance` | Cleanup, updates, operations |
| `setup` | Configuration, environment setup |

### Purposes (Be Specific)
| Purpose | Meaning |
|---------|---------|
| `test` | Run test suite |
| `lint` | Code quality/style checks |
| `type-check` | TypeScript/type validation |
| `build` | Compile/build code |
| `build-push` | Build AND push to registry |
| `deploy` | Deployment |
| `scan` | Security/dependency scanning |
| `validate` | General validation |
| `coverage` | Code coverage metrics |
| `benchmark` | Performance metrics |
| `cleanup` | Cleanup/maintenance tasks |

### Triggers (How It Starts)
| Trigger | Event | When |
|---------|-------|------|
| `push` | Git push to branch | Every commit |
| `pr` | Pull request event | PR opened/updated |
| `tag` | Git tag push | Version released |
| `manual` | workflow_dispatch | User clicks button |
| `scheduled` | Cron schedule | Time-based |
| `multi` | Multiple events | Various times |

### Frequencies (How Often)
| Frequency | Cadence | Use When |
|-----------|---------|----------|
| `per-commit` | Every git push | Fast, lightweight checks |
| `per-pr` | Each PR update | Code review gates |
| `hourly` | Every hour | Frequent monitoring |
| `nightly` | Once per night | Heavy operations |
| `weekly` | Once per week | Regular maintenance |
| `monthly` | Once per month | Infrequent tasks |
| `on-demand` | Manual only | Deployments, setup |

---

## ✅ Quick Examples

### CI Workflows
```
ci-test-push-per-commit.yml
  → Tests run on every commit to branch

ci-lint-pr-per-pr.yml
  → Linting on every PR update

ci-type-check-push-per-commit.yml
  → TypeScript checks on commits

ci-coverage-report-pr-per-pr.yml
  → Coverage report for PRs
```

### CD Workflows
```
cd-build-push-tag-on-demand.yml
  → Build image when tag pushed

cd-deploy-manual-on-demand.yml
  → Manual deployment trigger

cd-release-validation-tag-on-demand.yml
  → Validate release on tag
```

### Security Workflows
```
security-sast-push-nightly.yml
  → SAST scan nightly

security-deps-scan-scheduled-weekly.yml
  → Dependency audit weekly

security-container-scan-tag-on-demand.yml
  → Container image scan on build
```

### Maintenance Workflows
```
maintenance-cache-cleanup-scheduled-weekly.yml
  → Clear caches weekly

maintenance-deps-update-scheduled-weekly.yml
  → Update dependencies weekly

maintenance-logs-archive-scheduled-monthly.yml
  → Archive logs monthly
```

---

## 🚨 Common Mistakes

| ❌ Wrong | ✅ Correct | Why |
|---------|-----------|-----|
| `ci_test.yml` | `ci-test-push-per-commit.yml` | Use hyphens, specify context |
| `build-and-test.yml` | `ci-test-push-per-commit.yml` | Lead with category |
| `test.yml` | `ci-test-push-per-commit.yml` | Too generic |
| `ci-nightly-test.yml` | `ci-test-scheduled-nightly.yml` | Put trigger before frequency |
| `automated-deploy.yml` | `cd-deploy-manual-on-demand.yml` | Clear category and trigger |

---

## 🎓 Decision Tree

```
START
  ↓
What does it do?
  ├─→ Test/validate/lint? → Category: CI
  ├─→ Build/deploy? → Category: CD
  ├─→ Security/audit? → Category: SECURITY
  ├─→ Metrics/reporting? → Category: ANALYSIS
  ├─→ Environment setup? → Category: SETUP
  └─→ Maintenance/ops? → Category: MAINTENANCE
       ↓
    Pick SPECIFIC purpose
       ↓
    When does it run?
       ├─→ Every commit → Trigger: push
       ├─→ Every PR → Trigger: pr
       ├─→ Git tag → Trigger: tag
       ├─→ Cron schedule → Trigger: scheduled
       └─→ Manual button → Trigger: manual
            ↓
         How frequently?
            ├─→ Per commit → Frequency: per-commit
            ├─→ Per PR → Frequency: per-pr
            ├─→ Nightly → Frequency: nightly
            ├─→ Weekly → Frequency: weekly
            └─→ On-demand → Frequency: on-demand
                 ↓
         FILENAME READY!
```

---

## 📊 Your Project's Workflows (Current + Recommended)

| Old Name | New Name | Category | Purpose | Trigger | Frequency |
|----------|----------|----------|---------|---------|-----------|
| `ci.yml` | `ci-test-multi-per-commit.yml` | ci | test | push, pr, manual | per-commit |
| `fast-track.yml` | `ci-validation-pr-per-pr.yml` | ci | validation | pr | per-pr |
| `cd.yml` | `cd-deploy-manual-on-demand.yml` | cd | deploy | manual | on-demand |
| `cd-with-dockerhub.yml` | `cd-build-push-tag-on-demand.yml` | cd | build-push | tag | on-demand |
| `fast-track-tag-release.yml` | `cd-release-validation-tag-on-demand.yml` | cd | release-validation | tag | on-demand |
| `copilot-setup-steps.yml` | `setup-copilot-multi-on-demand.yml` | setup | copilot | multi | on-demand |

---

## ✨ Rules of Thumb

### ✅ DO

- ✅ Use **lowercase** with **hyphens**
- ✅ Put **category first** for alphabetical grouping
- ✅ Be **specific** about what it does
- ✅ Show **when** it runs (trigger)
- ✅ Indicate **frequency** (how often)
- ✅ Keep under **50 characters**
- ✅ Use **consistent terms** across workflows

### ❌ DON'T

- ❌ Use **underscores** or **camelCase**
- ❌ Be too **generic** (avoid `build.yml`)
- ❌ Mix naming **styles**
- ❌ Include **redundant words** (avoid "github-actions-")
- ❌ Make it **super long**
- ❌ Use non-standard **abbreviations**

---

## 🔍 Troubleshooting

**Q: My workflow does multiple things, what do I do?**  
A: Use the PRIMARY purpose. If equally important, split into separate workflows.

**Q: What if it triggers on different schedules?**  
A: Use `multi-trigger` or split into separate workflows.

**Q: Should I include the branch name?**  
A: No. The YAML file contains branch info. Filename shouldn't repeat it.

**Q: Can I use shorter names?**  
A: Only if they're clear. Example: `ci-test-push-per-commit.yml` is good, `ci-tst-p-pc.yml` is not.

**Q: What about deprecated workflows?**  
A: Prefix with `deprecated-`: `deprecated-ci-old-linter.yml`, then schedule removal.

---

## 📋 Validation Checklist

Before finalizing a workflow name:

- [ ] Category is **clear** (ci, cd, security, etc.)
- [ ] Purpose is **specific** (test, deploy, scan, etc.)
- [ ] Trigger is **explicit** (push, pr, tag, manual, scheduled)
- [ ] Frequency is **accurate** (per-commit, nightly, on-demand, etc.)
- [ ] Name is **≤50 characters**
- [ ] No **underscores** or **camelCase**
- [ ] Alphabetical **grouping works** (e.g., ci-*, cd-*, security-*)
- [ ] No **ambiguity** about what it does

---

## 🎁 Template for New Workflows

When creating a new workflow:

```yaml
name: [HUMAN-READABLE-NAME]
# Filename: [category]-[purpose]-[trigger]-[frequency].yml
# Example: ci-test-push-per-commit.yml

# Purpose: [One-line description]
# Triggers: [When this runs]
# Frequency: [How often]
# Duration: [Expected runtime]

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  # workflow_dispatch:  # Uncomment if manual trigger needed
  # schedule:
  #   - cron: '0 2 * * *'  # 2 AM daily

jobs:
  # ... your jobs here
```

---

## 📚 Full Documentation

For complete details:
- **[CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md)** - Full guide with examples
- **[WORKFLOW_RENAMING_GUIDE.md](./WORKFLOW_RENAMING_GUIDE.md)** - Step-by-step migration plan
- **[WORKFLOWS.md](./WORKFLOWS.md)** - Quick reference of your active workflows

---

## 💾 Print This!

This quick reference is perfect for:
- 📌 Printing and posting near your desk
- 📱 Adding to team wiki/Confluence
- 💬 Sharing in team Slack
- 📖 Including in onboarding docs

---

**Version:** 1.0  
**Last Updated:** 2026-09-14  
**Scope:** setupAppCreDepHelmPkg repository
