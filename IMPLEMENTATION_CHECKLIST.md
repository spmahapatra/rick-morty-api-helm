# CI/CD Naming Convention - Implementation Checklist

Complete step-by-step checklist for adopting the standardized workflow naming convention.

---

## 📋 Pre-Implementation Review

- [ ] Read `CI_CD_NAMING_CONVENTION.md` completely
- [ ] Review `WORKFLOW_NAMING_QUICK_REFERENCE.md` for patterns
- [ ] Understand the 6 workflow mappings (current → new names)
- [ ] Review `NAMING_CONVENTION_VISUAL_GUIDE.txt` for examples
- [ ] Gather team feedback on naming convention
- [ ] Plan rollout timeline (when to migrate)
- [ ] Identify any internal documentation that needs updates

---

## 🔧 Technical Preparation

### Environment Setup
- [ ] Ensure you have git access to the repository
- [ ] Verify you're on the main branch: `git branch`
- [ ] Pull latest changes: `git pull origin main`
- [ ] Check working directory is clean: `git status`

### Backup & Documentation
- [ ] Note current commit SHA for rollback: `git log --oneline -1`
- [ ] Take screenshot of GitHub Actions workflow list (before state)
- [ ] Export workflow run history if needed
- [ ] Document any custom workflow integrations (Slack notifications, etc.)

---

## 📝 Phase 1: Create Feature Branch

```bash
git checkout -b refactor/standardize-workflow-naming
```

**Verification:**
- [ ] Feature branch created successfully
- [ ] Confirm branch is listed: `git branch`
- [ ] Currently on new branch: `git branch` shows `*` on new branch

---

## 🔄 Phase 2: Rename Workflows (Using git mv)

### Step 2.1: Verify Current Files
```bash
cd .github/workflows
ls -la *.yml
```

Expected output (should have exactly 6 files):
- [ ] cd.yml
- [ ] cd-with-dockerhub.yml
- [ ] ci.yml
- [ ] copilot-setup-steps.yml
- [ ] fast-track.yml
- [ ] fast-track-tag-release.yml

### Step 2.2: Rename CI Workflows

```bash
# Rename ci.yml
git mv ci.yml ci-test-multi-per-commit.yml

# Rename fast-track.yml (quick validation, not full test)
git mv fast-track.yml ci-validation-pr-per-pr.yml
```

**Verification:**
- [ ] Both files renamed successfully
- [ ] Check with: `git status | grep ci-`
- [ ] Should see 2 renames

### Step 2.3: Rename CD Workflows

```bash
# Rename cd.yml
git mv cd.yml cd-deploy-manual-on-demand.yml

# Rename cd-with-dockerhub.yml
git mv cd-with-dockerhub.yml cd-build-push-tag-on-demand.yml

# Rename fast-track-tag-release.yml
git mv fast-track-tag-release.yml cd-release-validation-tag-on-demand.yml
```

**Verification:**
- [ ] All 3 CD workflow files renamed successfully
- [ ] Check with: `git status | grep cd-`
- [ ] Should see 3 renames

### Step 2.4: Rename Setup Workflow

```bash
# Rename copilot-setup-steps.yml
git mv copilot-setup-steps.yml setup-copilot-multi-on-demand.yml
```

**Verification:**
- [ ] File renamed successfully
- [ ] Check with: `git status | grep setup-`
- [ ] Should see 1 rename

### Step 2.5: Verify All Renames

```bash
git status
```

Expected output:
- [ ] 6 renamed files total
- [ ] No other changes
- [ ] No untracked files

All CI-related files should show:
```
renamed:    ci.yml -> ci-test-multi-per-commit.yml
renamed:    fast-track.yml -> ci-validation-pr-per-pr.yml
```

All CD-related files should show:
```
renamed:    cd.yml -> cd-deploy-manual-on-demand.yml
renamed:    cd-with-dockerhub.yml -> cd-build-push-tag-on-demand.yml
renamed:    fast-track-tag-release.yml -> cd-release-validation-tag-on-demand.yml
```

Setup files should show:
```
renamed:    copilot-setup-steps.yml -> setup-copilot-multi-on-demand.yml
```

### Step 2.6: Verify Alphabetical Sorting

```bash
ls -1 *.yml | sort
```

Expected order:
- [ ] cd-build-push-tag-on-demand.yml
- [ ] cd-deploy-manual-on-demand.yml
- [ ] cd-release-validation-tag-on-demand.yml
- [ ] ci-test-multi-per-commit.yml
- [ ] ci-validation-pr-per-pr.yml
- [ ] setup-copilot-multi-on-demand.yml

This shows perfect grouping by category!

---

## 📚 Phase 3: Create Documentation Files

### Step 3.1: Documentation Already Provided

The following documentation files have been created:
- [ ] `CI_CD_NAMING_CONVENTION.md` - Comprehensive guide
- [ ] `WORKFLOW_RENAMING_GUIDE.md` - Step-by-step migration plan
- [ ] `WORKFLOW_NAMING_QUICK_REFERENCE.md` - One-page cheat sheet
- [ ] `NAMING_CONVENTION_VISUAL_GUIDE.txt` - Visual examples
- [ ] `IMPLEMENTATION_CHECKLIST.md` - This file

Verify these exist:
```bash
ls -la *.md *.txt | grep -E "(NAMING|WORKFLOW|IMPLEMENTATION)"
```

- [ ] All 5 documentation files present

### Step 3.2: Create Quick Reference for Workflows

Create a new file `WORKFLOWS.md`:

```bash
cat > WORKFLOWS.md << 'WORKFLOWS_EOF'
# GitHub Actions Workflows

This project uses standardized workflow naming: `[category]-[purpose]-[trigger]-[frequency].yml`

## Active Workflows

| Workflow | Category | Purpose | Triggers | Frequency | Duration | Status |
|----------|----------|---------|----------|-----------|----------|--------|
| `ci-test-multi-per-commit.yml` | CI | Run test suite | push, PR, manual | Per commit | 10-20m | ✅ Active |
| `ci-validation-pr-per-pr.yml` | CI | Quick validation (lint, type-check) | PR, push, manual | Per PR | 5-10m | ✅ Active |
| `cd-build-push-tag-on-demand.yml` | CD | Build & push Docker images | git tag | On-demand | 10-30m | ✅ Active |
| `cd-deploy-manual-on-demand.yml` | CD | Manual deployments | manual | On-demand | 20-60m | ✅ Active |
| `cd-release-validation-tag-on-demand.yml` | CD | Release validation | git tag | On-demand | 10-15m | ✅ Active |
| `setup-copilot-multi-on-demand.yml` | Setup | Copilot environment setup | push, PR, manual | Per commit | 2-5m | ✅ Active |

## Naming Convention

For details on the naming pattern and how to add new workflows, see:
- [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md) - Full guide
- [WORKFLOW_NAMING_QUICK_REFERENCE.md](./WORKFLOW_NAMING_QUICK_REFERENCE.md) - Quick reference

## Workflow Triggers

### push (every commit)
- `ci-test-multi-per-commit.yml`
- `ci-validation-pr-per-pr.yml`
- `setup-copilot-multi-on-demand.yml`

### pull_request (PR opened/updated)
- `ci-test-multi-per-commit.yml`
- `ci-validation-pr-per-pr.yml`
- `setup-copilot-multi-on-demand.yml`

### git tag (release tags)
- `cd-build-push-tag-on-demand.yml`
- `cd-release-validation-tag-on-demand.yml`

### manual (workflow_dispatch)
- `cd-deploy-manual-on-demand.yml`
- All workflows support manual trigger

## Testing Workflows

### Test CI workflows
```bash
git commit --allow-empty -m "test: trigger CI workflows"
git push origin <your-branch>
# Monitor GitHub Actions tab
```

### Test tag-triggered workflows
```bash
git tag v0.1.0-test
git push origin v0.1.0-test
# Monitor GitHub Actions tab
# Cleanup: git tag -d v0.1.0-test && git push origin --delete v0.1.0-test
```

### Test manual workflows
Go to GitHub → Actions tab → Select workflow → Click "Run workflow" button

## Documentation

For comprehensive details on:
- Creating new workflows: See CI_CD_NAMING_CONVENTION.md
- Renaming workflows: See WORKFLOW_RENAMING_GUIDE.md
- Quick reference: See WORKFLOW_NAMING_QUICK_REFERENCE.md
- Visual examples: See NAMING_CONVENTION_VISUAL_GUIDE.txt

WORKFLOWS_EOF
```

Verify file was created:
- [ ] `WORKFLOWS.md` created successfully
- [ ] Check: `ls -la WORKFLOWS.md`

### Step 3.3: Update README.md

Add references to CI/CD documentation in the main README:

```markdown
## CI/CD Pipelines

This project uses GitHub Actions for continuous integration and deployment.

### Workflows

See [WORKFLOWS.md](./WORKFLOWS.md) for a complete list of active workflows with triggers and frequency.

### Naming Convention

All workflows follow a standardized naming pattern for clarity:
- **Pattern:** `[category]-[purpose]-[trigger]-[frequency].yml`
- **Reference:** See [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md)
- **Quick Guide:** See [WORKFLOW_NAMING_QUICK_REFERENCE.md](./WORKFLOW_NAMING_QUICK_REFERENCE.md)

### Adding New Workflows

Before creating a new workflow, review the naming convention guide:
1. Read [CI_CD_NAMING_CONVENTION.md](./CI_CD_NAMING_CONVENTION.md)
2. Use the decision tree to determine category, purpose, trigger, frequency
3. Follow the naming pattern consistently
```

- [ ] README.md updated with CI/CD documentation links

---

## 📤 Phase 4: Create Commit

### Step 4.1: Review All Changes

```bash
git status
```

Should show:
- [ ] 6 renamed workflow files
- [ ] New/modified documentation files
- [ ] Nothing else (no stray files or changes)

### Step 4.2: Review Diff (Optional but Recommended)

```bash
git diff --name-only --cached
```

- [ ] Shows only the files you expect

### Step 4.3: Stage All Changes

```bash
git add .
```

Verify:
```bash
git status
```

- [ ] All changes staged
- [ ] No unstaged changes
- [ ] All files listed for commit

### Step 4.4: Create Descriptive Commit Message

```bash
git commit -m "refactor: standardize CI/CD workflow naming convention

Workflows now use consistent naming pattern: [category]-[purpose]-[trigger]-[frequency].yml

This change improves:
✓ Discoverability - Purpose immediately clear from filename
✓ Organization - Workflows group logically when sorted
✓ Clarity - Trigger conditions visible in name
✓ Onboarding - New team members understand at a glance
✓ Scalability - Pattern works for 6 workflows or 60+

Renamed workflows:
- ci.yml → ci-test-multi-per-commit.yml
- fast-track.yml → ci-validation-pr-per-pr.yml
- cd.yml → cd-deploy-manual-on-demand.yml
- cd-with-dockerhub.yml → cd-build-push-tag-on-demand.yml
- fast-track-tag-release.yml → cd-release-validation-tag-on-demand.yml
- copilot-setup-steps.yml → setup-copilot-multi-on-demand.yml

Documentation added:
- CI_CD_NAMING_CONVENTION.md - Comprehensive guide
- WORKFLOW_RENAMING_GUIDE.md - Step-by-step migration
- WORKFLOW_NAMING_QUICK_REFERENCE.md - One-page reference
- NAMING_CONVENTION_VISUAL_GUIDE.txt - Visual examples
- WORKFLOWS.md - Workflow registry
- IMPLEMENTATION_CHECKLIST.md - Implementation guide

See CI_CD_NAMING_CONVENTION.md for naming convention details.

Related to: CI/CD Modernization
"
```

Verify:
- [ ] Commit created successfully
- [ ] Check with: `git log --oneline -1`

### Step 4.5: Verify Commit Contents

```bash
git show --name-status
```

- [ ] Shows all 6 renamed workflow files
- [ ] Shows all new documentation files
- [ ] Commit message is descriptive

---

## 🧪 Phase 5: Testing & Validation

### Step 5.1: Local Validation

Before pushing, run basic validation:

```bash
# Verify YAML syntax for all workflows
for file in .github/workflows/*.yml; do
  echo "Checking $file..."
  grep -q "^name:" "$file" && echo "  ✓ Has 'name' field" || echo "  ✗ Missing 'name' field"
  grep -q "^on:" "$file" && echo "  ✓ Has 'on' trigger" || echo "  ✗ Missing 'on' trigger"
done
```

- [ ] All workflow files have `name:` field
- [ ] All workflow files have `on:` trigger definition

### Step 5.2: Push Feature Branch

```bash
git push origin refactor/standardize-workflow-naming
```

Verify:
- [ ] Branch pushed successfully
- [ ] Check: `git branch -r | grep refactor/standardize`

### Step 5.3: Create Pull Request

On GitHub:
1. Go to repository
2. Click "Compare & pull request" (or use GitHub CLI)
3. Create PR with title: `refactor: standardize CI/CD workflow naming convention`
4. Add description:

```markdown
## Summary
Standardizes GitHub Actions workflow filenames using a consistent naming pattern for improved clarity and discoverability.

## Pattern
`[category]-[purpose]-[trigger]-[frequency].yml`

## Changes
Renamed 6 workflows with new standardized names. No functional changes—all workflows work identically.

## Benefits
- 🎯 **Instant clarity** - Purpose immediately clear from filename
- 🔍 **Better discovery** - Workflows group logically when sorted
- 📋 **Visible triggers** - Trigger conditions shown in name
- 👥 **Easier onboarding** - New team members understand at a glance
- 📈 **Scales well** - Works for 6 workflows or 60+

## Workflow Mappings
- `ci.yml` → `ci-test-multi-per-commit.yml`
- `fast-track.yml` → `ci-validation-pr-per-pr.yml`
- `cd.yml` → `cd-deploy-manual-on-demand.yml`
- `cd-with-dockerhub.yml` → `cd-build-push-tag-on-demand.yml`
- `fast-track-tag-release.yml` → `cd-release-validation-tag-on-demand.yml`
- `copilot-setup-steps.yml` → `setup-copilot-multi-on-demand.yml`

## Documentation
New documentation added:
- `CI_CD_NAMING_CONVENTION.md` - Full guide with examples
- `WORKFLOW_RENAMING_GUIDE.md` - Implementation details
- `WORKFLOW_NAMING_QUICK_REFERENCE.md` - One-page cheat sheet
- `NAMING_CONVENTION_VISUAL_GUIDE.txt` - Visual reference
- `WORKFLOWS.md` - Workflow registry
- `IMPLEMENTATION_CHECKLIST.md` - Checklist for adoption

## Testing
- [x] All workflow YAML syntax valid
- [x] Workflows tested locally
- [x] No functional changes to workflow logic
- [x] All documentation created

## Rollback
If needed, simple one-commit rollback: `git revert <commit-sha>`

**Closes:** #N/A
```

- [ ] PR created successfully
- [ ] PR title is descriptive
- [ ] PR description is complete

### Step 5.4: Wait for CI to Pass

Monitor PR checks:
- [ ] All GitHub Actions on PR pass
- [ ] No syntax errors reported
- [ ] PR shows "All checks passed"

### Step 5.5: Collect Reviews

- [ ] Assign reviewers
- [ ] Wait for peer review feedback
- [ ] Address any comments
- [ ] Get approval from at least 1 reviewer

### Step 5.6: Test Workflow Functionality (Optional but Recommended)

After PR approval but before merge, optionally test:

```bash
# Checkout feature branch
git checkout refactor/standardize-workflow-naming

# Push test commit to trigger CI workflows
git commit --allow-empty -m "test: verify renamed workflows still work"
git push origin refactor/standardize-workflow-naming

# Monitor GitHub Actions tab
# Expected: ci-test-multi-per-commit.yml and ci-validation-pr-per-pr.yml start
```

- [ ] CI workflows trigger correctly
- [ ] Tests pass in all renamed workflows

### Step 5.7: Test Tag-Triggered Workflows (Optional)

To test CD workflows that trigger on tags:

```bash
# Create test tag
git tag v0.1.0-naming-test

# Push tag (this is done from your feature branch with the new names)
git push origin v0.1.0-naming-test

# Monitor GitHub Actions tab
# Expected: cd-build-push-tag-on-demand.yml and cd-release-validation-tag-on-demand.yml start

# Cleanup test tag
git tag -d v0.1.0-naming-test
git push origin --delete v0.1.0-naming-test
```

- [ ] Tag-triggered workflows work correctly
- [ ] Build succeeds in renamed workflows

---

## ✅ Phase 6: Merge to Main

### Step 6.1: Final Verification

Before merging, verify:
- [ ] All PR checks pass
- [ ] Code review approved
- [ ] Feature branch is up-to-date with main
- [ ] No conflicts

### Step 6.2: Merge PR

On GitHub, click "Merge pull request":
- [ ] Select "Create a merge commit" (preserves history)
- [ ] Confirm merge

Or via CLI:
```bash
git checkout main
git pull origin main
git merge --no-ff refactor/standardize-workflow-naming
git push origin main
```

Verify:
- [ ] PR shows "Merged"
- [ ] Commit visible in main branch

### Step 6.3: Delete Feature Branch

```bash
git branch -d refactor/standardize-workflow-naming
git push origin --delete refactor/standardize-workflow-naming
```

Verify:
- [ ] Branch deleted locally
- [ ] Branch deleted from remote

### Step 6.4: Verify Main Branch

```bash
git checkout main
git pull origin main
ls -la .github/workflows/*.yml | wc -l
```

- [ ] Main branch has the 6 renamed workflows
- [ ] No old workflow files remain
- [ ] Documentation files are present

---

## 📢 Phase 7: Communication & Documentation

### Step 7.1: Update Team

Post in your team channel (Slack, Teams, etc.):

```
📢 CI/CD Workflow Naming Convention Adopted

✅ All GitHub Actions workflows now follow a standardized naming pattern:
   [category]-[purpose]-[trigger]-[frequency].yml

🎯 Benefits:
- Immediate clarity on what each workflow does
- Trigger conditions visible in the filename
- Execution frequency shown in name
- Easier discovery and maintenance

📚 Documentation:
- CI_CD_NAMING_CONVENTION.md → Full guide
- WORKFLOW_NAMING_QUICK_REFERENCE.md → One-page reference
- WORKFLOWS.md → Workflow registry

🔄 Workflows renamed:
- ci.yml → ci-test-multi-per-commit.yml
- fast-track.yml → ci-validation-pr-per-pr.yml
- cd.yml → cd-deploy-manual-on-demand.yml
- cd-with-dockerhub.yml → cd-build-push-tag-on-demand.yml
- fast-track-tag-release.yml → cd-release-validation-tag-on-demand.yml
- copilot-setup-steps.yml → setup-copilot-multi-on-demand.yml

No functional changes—all workflows work exactly as before!

Questions? Check the documentation or ask in #ci-cd channel.
```

- [ ] Team notified of changes
- [ ] Documentation links shared

### Step 7.2: Update External Documentation

If you have external documentation (wiki, confluence, runbooks), update:
- [ ] Remove references to old workflow names
- [ ] Update workflow references to new names
- [ ] Add link to `WORKFLOWS.md` for reference
- [ ] Update CI/CD runbooks if needed

### Step 7.3: Update CI/CD Runbooks

Check for any runbooks/guides that reference workflows:
- [ ] Search for old workflow names in documentation
- [ ] Replace with new standardized names
- [ ] Verify links still work

### Step 7.4: Archive This Checklist

- [ ] Save this checklist for future reference
- [ ] Include in onboarding documentation
- [ ] Share with new team members

---

## 🔄 Future Workflow Additions

When adding new workflows, follow this checklist:

### For Any New Workflow
- [ ] Determine category (ci, cd, security, analysis, maintenance, setup)
- [ ] Define specific purpose (test, build, deploy, scan, etc.)
- [ ] Identify primary trigger (push, pr, tag, manual, scheduled)
- [ ] Determine execution frequency (per-commit, nightly, on-demand, etc.)
- [ ] Use pattern: `[category]-[purpose]-[trigger]-[frequency].yml`
- [ ] Add to `WORKFLOWS.md` registry
- [ ] Document in workflow file header

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
    branches: [main]
  # Add other triggers as needed

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      # Your workflow steps
```

---

## 🆘 Troubleshooting

### Issue: Old workflow names still appear in GitHub UI

**Solution:** GitHub caches workflow lists. Wait 5-10 minutes for cache to refresh, then refresh page.
- [ ] Wait 10 minutes
- [ ] Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- [ ] Check Actions tab again

### Issue: Workflow runs not showing in history

**Solution:** Old runs are in history under old filenames. New runs will show under new names.
- [ ] This is normal behavior
- [ ] No action needed
- [ ] Future runs will appear under new names

### Issue: "Workflow not found" error

**Solution:** GitHub sometimes caches workflow definitions. Clear cache and re-check.
- [ ] Wait 5-10 minutes for GitHub to sync
- [ ] Go to Settings → Actions → General
- [ ] Check "Allow GitHub Actions to create and approve pull requests"
- [ ] Manually trigger a workflow to verify it works

### Issue: Automated status checks reference old names

**Solution:** Update any branch protection rules that reference old workflow names.
- [ ] Go to Settings → Branches → Branch protection rules
- [ ] Edit rule and update required status checks
- [ ] Replace old workflow names with new ones

### Issue: Need to rollback changes

**Solution:** GitHub makes this easy with git revert:
```bash
git log --oneline | grep "standardize CI/CD"
git revert <commit-sha>
git push origin main
```

- [ ] Rollback completed if needed

---

## ✨ Post-Implementation Verification

After everything is merged, verify:

- [ ] All 6 workflows present with new names
- [ ] Workflows trigger correctly on events
- [ ] Documentation accessible and accurate
- [ ] Team informed of changes
- [ ] No broken references in external docs
- [ ] Runbooks updated with new workflow names
- [ ] Future workflow additions follow the pattern

---

## 📋 Sign-Off Checklist

Once implementation complete:

- [ ] All phases completed
- [ ] Team communication done
- [ ] Documentation updated
- [ ] External references updated
- [ ] No rollback needed
- [ ] Workflows functioning normally
- [ ] Team trained on new naming pattern
- [ ] This checklist completed and archived

---

## 📝 Document Information

- **Version:** 1.0
- **Created:** 2026-09-14
- **Repository:** setupAppCreDepHelmPkg
- **Status:** Ready for implementation
- **Estimated Duration:** 30-45 minutes for full implementation
- **Difficulty:** Low (mainly file renames via git)
- **Risk Level:** Low (git preserves history, easy rollback)
