# CI/CD Workflow Renaming - Implementation Plan

Detailed step-by-step plan to migrate your repository to the standardized CI/CD naming convention.

---

## 📊 Current Workflows → New Names Mapping

### Analysis of Current Workflows

| Current Name | Issues | Category | Purpose | Trigger | Frequency | **Recommended Name** |
|---|---|---|---|---|---|---|
| `ci.yml` | Generic | ci | test | push, pr, manual | per-commit | **ci-test-multi-per-commit.yml** |
| `fast-track.yml` | Vague purpose | ci | validation | pr, push, manual | per-pr | **ci-validation-pr-per-pr.yml** |
| `cd.yml` | Generic | cd | deploy | manual | on-demand | **cd-deploy-manual-on-demand.yml** |
| `cd-with-dockerhub.yml` | Unclear trigger | cd | build, push | tag | on-demand | **cd-build-push-tag-on-demand.yml** |
| `fast-track-tag-release.yml` | Vague | cd | release-validation | tag | on-demand | **cd-release-validation-tag-on-demand.yml** |
| `copilot-setup-steps.yml` | Not CI/CD specific | setup | copilot | pr, push, manual | multi-trigger | **setup-copilot-multi-on-demand.yml** |

---

## 🔍 Workflow Details & Recommendations

### 1. ci.yml → ci-test-multi-per-commit.yml

**Current Configuration:**
```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop, feature/*]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
```

**Analysis:**
- Runs comprehensive tests on every commit
- Triggered by: push (all branches) + PR + manual
- Frequency: Multiple times per day (per-commit)
- Duration: 10-20 minutes

**Recommended Name:** `ci-test-multi-per-commit.yml`
- **Category:** `ci` (Continuous Integration)
- **Purpose:** `test` (runs test suite)
- **Trigger:** `multi` (push + PR + manual)
- **Frequency:** `per-commit` (every code change)

**Rationale:**
- "Multi" clarifies it responds to multiple trigger types
- "Per-commit" indicates high frequency (not nightly or on-demand)
- "Test" emphasizes it's validation, not deployment

---

### 2. fast-track.yml → ci-validation-pr-per-pr.yml

**Current Configuration:**
```yaml
name: Fast Track Validation
on:
  pull_request:
  push:
  workflow_dispatch:
```

**Analysis:**
- Runs quick validation checks (lint, type-check)
- Triggered by: PR + push + manual
- Frequency: Per pull request or per commit
- Duration: 5-10 minutes
- Purpose: Fast feedback loop (hence "fast-track")

**Recommended Name:** `ci-validation-pr-per-pr.yml`
- **Category:** `ci` (Continuous Integration)
- **Purpose:** `validation` (performs quick validation checks)
- **Trigger:** `pr` (primarily PR-triggered)
- **Frequency:** `per-pr` (on every PR update)

**Rationale:**
- "Validation" is more specific than "fast-track" (describes what it does)
- "PR" primary because that's the main use (code review gate)
- "Per-PR" indicates it runs frequently but not per-commit

---

### 3. cd.yml → cd-deploy-manual-on-demand.yml

**Current Configuration:**
```yaml
name: CD Pipeline
on:
  workflow_dispatch:
```

**Analysis:**
- Handles deployments
- Triggered by: manual only (workflow_dispatch)
- Frequency: On-demand when user clicks "Run"
- Duration: 20-60 minutes (multi-stage deployment)

**Recommended Name:** `cd-deploy-manual-on-demand.yml`
- **Category:** `cd` (Continuous Deployment)
- **Purpose:** `deploy` (performs deployments)
- **Trigger:** `manual` (workflow_dispatch only)
- **Frequency:** `on-demand` (no scheduled/automatic runs)

**Rationale:**
- "Deploy" clearly indicates deployment action
- "Manual" shows it's not automatic (requires user action)
- "On-demand" reinforces that it's operator-initiated

---

### 4. cd-with-dockerhub.yml → cd-build-push-tag-on-demand.yml

**Current Configuration:**
```yaml
name: CD Pipeline - Docker Hub Push
on:
  workflow_dispatch:
  # Triggered when git tag is pushed (v*.*)
```

**Analysis:**
- Builds Docker images and pushes to registries (GHCR + Docker Hub)
- Triggered by: git tag push (implicit via workflow config)
- Frequency: On-demand via tag push
- Duration: 10-30 minutes (multi-platform builds)
- Current name "with-dockerhub" is too vague

**Recommended Name:** `cd-build-push-tag-on-demand.yml`
- **Category:** `cd` (Continuous Deployment)
- **Purpose:** `build-push` (build images and push to registry)
- **Trigger:** `tag` (when version tags are pushed)
- **Frequency:** `on-demand` (developer initiates via git tag)

**Rationale:**
- "Build-push" explicitly states the two main actions
- "Tag" shows it's tag-triggered (not branch-triggered)
- "On-demand" indicates developer action (tagging) triggers it
- Replaces vague "with-dockerhub" reference

---

### 5. fast-track-tag-release.yml → cd-release-validation-tag-on-demand.yml

**Current Configuration:**
```yaml
name: Fast Track Release Validation
on:
  workflow_dispatch:
  # Triggered on release tags
```

**Analysis:**
- Validates release before deployment
- Triggered by: git tag push (release tags)
- Frequency: On-demand via tag push
- Duration: 10-15 minutes
- Purpose: Pre-release validation (syntax, tests, docker-compose)

**Recommended Name:** `cd-release-validation-tag-on-demand.yml`
- **Category:** `cd` (Continuous Deployment)
- **Purpose:** `release-validation` (validates release candidate)
- **Trigger:** `tag` (when release tags pushed)
- **Frequency:** `on-demand` (developer-initiated via tag)

**Rationale:**
- "Release-validation" explains purpose better than "fast-track"
- "Tag" shows tag-triggered
- "On-demand" emphasizes manual workflow
- Distinguishes from `cd-build-push-tag-on-demand.yml` (different purpose)

---

### 6. copilot-setup-steps.yml → setup-copilot-multi-on-demand.yml

**Current Configuration:**
```yaml
name: "Copilot Setup Steps"
on:
  workflow_dispatch:
  push:
  pull_request:
```

**Analysis:**
- Sets up Copilot environment/configuration
- Triggered by: push + PR + manual
- Frequency: Per-commit + on-demand
- Duration: 2-5 minutes
- Purpose: Environment/tooling setup (not typical CI/CD)

**Recommended Name:** `setup-copilot-multi-on-demand.yml`
- **Category:** `setup` (Configuration/Setup)
- **Purpose:** `copilot` (Copilot-specific setup)
- **Trigger:** `multi` (multiple trigger types)
- **Frequency:** `on-demand` (primarily manual, though also auto-trigger)

**Rationale:**
- Separate "setup" category (not CI or CD)
- Distinguishes from typical CI/CD workflows
- "Copilot" makes purpose specific
- "Multi" shows multiple triggers

---

## 🚀 Migration Steps

### Phase 1: Preparation (No Code Changes)

**Step 1.1: Create a feature branch**
```bash
git checkout -b refactor/standardize-workflow-naming
```

**Step 1.2: Review all workflows**
```bash
cd .github/workflows
ls -la *.yml
# Verify all 6 files match the analysis above
```

**Step 1.3: Document current state**
```bash
# Create a backup reference
git log --oneline -5  # Note the current commit SHA
```

### Phase 2: Rename Workflows (Git Move)

Use `git mv` to preserve history and tracking:

**Step 2.1: Rename CI workflows**
```bash
git mv .github/workflows/ci.yml .github/workflows/ci-test-multi-per-commit.yml
git mv .github/workflows/fast-track.yml .github/workflows/ci-validation-pr-per-pr.yml
```

**Step 2.2: Rename CD workflows**
```bash
git mv .github/workflows/cd.yml .github/workflows/cd-deploy-manual-on-demand.yml
git mv .github/workflows/cd-with-dockerhub.yml .github/workflows/cd-build-push-tag-on-demand.yml
git mv .github/workflows/fast-track-tag-release.yml .github/workflows/cd-release-validation-tag-on-demand.yml
```

**Step 2.3: Rename setup workflow**
```bash
git mv .github/workflows/copilot-setup-steps.yml .github/workflows/setup-copilot-multi-on-demand.yml
```

**Step 2.4: Verify rename success**
```bash
git status
# Should show 6 renames:
# M  .github/workflows/ci-test-multi-per-commit.yml
# M  .github/workflows/ci-validation-pr-per-pr.yml
# ...etc
```

### Phase 3: Update Documentation

**Step 3.1: Create WORKFLOWS.md reference**
```markdown
# GitHub Actions Workflows

This project uses standardized workflow naming: `[category]-[purpose]-[trigger]-[frequency].yml`

## Active Workflows

| Workflow | Purpose | Triggers | Frequency | Duration |
|----------|---------|----------|-----------|----------|
| ci-test-multi-per-commit.yml | Run test suite | push, PR, manual | Per commit | 10-20m |
| ci-validation-pr-per-pr.yml | Quick validation (lint, type-check) | PR, push, manual | Per PR | 5-10m |
| cd-deploy-manual-on-demand.yml | Manual deployments | manual | On-demand | 20-60m |
| cd-build-push-tag-on-demand.yml | Build & push Docker images | git tag | On-demand | 10-30m |
| cd-release-validation-tag-on-demand.yml | Release validation | git tag | On-demand | 10-15m |
| setup-copilot-multi-on-demand.yml | Copilot environment setup | push, PR, manual | Per commit | 2-5m |

See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) for naming details.
```

**Step 3.2: Update README.md**
Add reference to workflow documentation:
```markdown
## CI/CD Pipelines

All GitHub Actions workflows follow a standardized naming convention for clarity.

- See [WORKFLOWS.md](./WORKFLOWS.md) for active workflows
- See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) for naming details
```

**Step 3.3: Update PIPELINE_FIXES.md**
Add section linking to new naming convention:
```markdown
## Workflow Naming

As part of modernizing the CI/CD infrastructure, all workflows now follow a standardized naming convention. See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) for details.
```

### Phase 4: Commit Changes

**Step 4.1: Stage all changes**
```bash
git add .github/workflows/
git add CI_CD_NAMING_CONVENTION.md
git add WORKFLOWS.md
git add README.md
git add PIPELINE_FIXES.md
```

**Step 4.2: Create descriptive commit**
```bash
git commit -m "refactor: standardize CI/CD workflow naming convention

Workflows now use consistent naming pattern: [category]-[purpose]-[trigger]-[frequency].yml

Renamed workflows:
- ci.yml → ci-test-multi-per-commit.yml
- fast-track.yml → ci-validation-pr-per-pr.yml
- cd.yml → cd-deploy-manual-on-demand.yml
- cd-with-dockerhub.yml → cd-build-push-tag-on-demand.yml
- fast-track-tag-release.yml → cd-release-validation-tag-on-demand.yml
- copilot-setup-steps.yml → setup-copilot-multi-on-demand.yml

Benefits:
- Improved discoverability and clarity
- Self-documenting workflow purposes
- Consistent organization and sorting
- Easier onboarding for new team members

See CI_CD_NAMING_CONVENTION.md for complete details."
```

### Phase 5: Testing & Validation

**Step 5.1: Verify workflow execution**

After merging, test that workflows still trigger correctly:

```bash
# Test 1: Push to main (triggers per-commit workflows)
git push origin refactor/standardize-workflow-naming

# Check GitHub Actions dashboard
# Expected: ci-test-multi-per-commit.yml and ci-validation-pr-per-pr.yml start

# Test 2: Create and push a test tag (triggers tag workflows)
git tag v0.1.0-naming-test
git push origin v0.1.0-naming-test

# Check GitHub Actions dashboard
# Expected: cd-build-push-tag-on-demand.yml and cd-release-validation-tag-on-demand.yml start

# Cleanup test tag
git tag -d v0.1.0-naming-test
git push origin --delete v0.1.0-naming-test
```

**Step 5.2: Verify workflow names in UI**

1. Go to GitHub repo → Actions tab
2. Verify all workflows appear with new names
3. Click each workflow to confirm it runs correctly
4. Check workflow history shows no broken runs

**Step 5.3: Verify GitHub Actions links**

Update any hardcoded links or documentation references:

- [ ] Update GitHub Pages docs (if any)
- [ ] Update team wiki/confluence (if external docs)
- [ ] Update CI/CD runbooks
- [ ] Inform team of naming change

### Phase 6: Merge & Communication

**Step 6.1: Create Pull Request**
```bash
git push origin refactor/standardize-workflow-naming
# Create PR with title: "refactor: standardize CI/CD workflow naming convention"
```

**Step 6.2: Add PR Description**
```markdown
## Summary
Standardizes GitHub Actions workflow filenames using a consistent naming pattern:
`[category]-[purpose]-[trigger]-[frequency].yml`

## Changes
- Renamed 6 workflows for improved clarity and discoverability
- Added comprehensive naming convention documentation
- Updated workflow reference guide

## Benefits
- 🎯 Instant clarity on workflow purpose
- 🔍 Easier discovery and maintenance
- 📚 Self-documenting workflow organization
- 👥 Better onboarding for new team members
- 📈 Scales well as CI/CD grows

## Migration Details
See commit message for detailed rename mapping.

## Testing
- [x] All workflows tested with commits and tags
- [x] No broken workflow runs
- [x] Workflow names display correctly in UI
- [x] Documentation updated

Fixes #N/A
Related to: CI/CD Modernization effort
```

**Step 6.3: Get review & merge**
```bash
# After approval
git checkout main
git merge --no-ff refactor/standardize-workflow-naming
git push origin main
```

**Step 6.4: Announce to team**
```markdown
## 📢 Workflow Naming Convention Adopted

We've standardized our GitHub Actions workflow naming for improved clarity!

### New Pattern
`[category]-[purpose]-[trigger]-[frequency].yml`

### Examples
- `ci-test-multi-per-commit.yml` - Runs tests on every commit
- `cd-build-push-tag-on-demand.yml` - Builds & pushes images on tag
- `security-scan-scheduled-weekly.yml` - Weekly security scan

### What Changed
6 workflows renamed to follow the standard. No functional changes—all workflows work identically.

### Documentation
- See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) for complete guide
- See [WORKFLOWS.md](./WORKFLOWS.md) for quick reference

Questions? Check the docs or ask in #ci-cd channel!
```

---

## 🔄 Rollback Plan (If Needed)

If issues arise, rollback is simple:

```bash
# Revert commit
git revert <commit-sha>
git push origin main

# Or reset entire branch
git reset --hard <previous-commit>
git push origin main -f  # Use with caution!
```

---

## 📋 Checklist for Implementation

### Preparation Phase
- [ ] Read CI_CD_NAMING_CONVENTION.md completely
- [ ] Understand mapping of current → new names
- [ ] Back up any local workflow customizations
- [ ] Notify team of planned changes

### Execution Phase
- [ ] Create feature branch
- [ ] Rename all 6 workflows using `git mv`
- [ ] Create/update documentation files
- [ ] Review `git status` shows all expected changes
- [ ] Create descriptive commit message

### Testing Phase
- [ ] Push feature branch and create PR
- [ ] Verify no syntax errors in workflows
- [ ] Test CI trigger with push commit
- [ ] Test CD trigger with tag push
- [ ] Check GitHub Actions UI shows new names
- [ ] Verify workflow history looks good

### Finalization Phase
- [ ] Get peer review on PR
- [ ] Address any review comments
- [ ] Merge to main branch
- [ ] Announce changes to team
- [ ] Document in team wiki/docs
- [ ] Update any external CI/CD documentation

---

## 💡 Tips for Success

1. **Do it in one commit** - Rename all at once so history is clean
2. **Use git mv** - Preserves file history better than delete/create
3. **Test immediately after** - Verify workflows trigger correctly
4. **Update docs in same commit** - Keep everything synchronized
5. **Communicate clearly** - Help team understand the changes
6. **No functional changes** - Only renaming, so no risk of breaking functionality

---

## 📝 Future Workflow Checklist

When adding NEW workflows, use this checklist:

- [ ] Determine category (ci, cd, security, analysis, maintenance, setup)
- [ ] Define specific purpose (test, build, deploy, scan, etc.)
- [ ] Identify primary trigger (push, pr, tag, schedule, manual)
- [ ] Determine execution frequency (per-commit, per-pr, nightly, weekly, on-demand)
- [ ] Create filename: `[category]-[purpose]-[trigger]-[frequency].yml`
- [ ] Name in YAML matches filename (best practice)
- [ ] Add to WORKFLOWS.md reference table
- [ ] Document in workflow file header

---

## 📞 Support & Questions

If you have questions about:
- **Naming convention**: See CI_CD_NAMING_CONVENTION.md
- **Specific workflow**: See WORKFLOWS.md
- **How to apply**: See this implementation guide
- **Edge cases**: Check FAQ section in convention document

---

## 📄 Document Information

- **Version:** 1.0
- **Created:** 2026-09-14
- **Applicable To:** setupAppCreDepHelmPkg repository
- **Status:** Ready for implementation
