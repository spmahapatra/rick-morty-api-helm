# Tag-Based Deployment Workflow

## Overview

The CI/CD pipeline now triggers exclusively on **tag creation** rather than on git push events. This ensures that:
- All changes are reviewed locally before any automation runs
- Deployment is only triggered after explicit tag creation
- Manual verification happens before final commit and push
- Clear separation between development and deployment workflows

## Workflow Trigger Model

### Previous Model (Deprecated)
```
Push to branch → CI runs → CD runs (automatic)
❌ No local review opportunity
```

### New Model (Current)
```
Local Development → Local Review → Tag Creation → CI/CD Runs
✅ Explicit local verification before automation
```

## Step-by-Step Process

### 1. Development & Local Testing

Make your changes and test locally:

```bash
# Make changes to your code
git add .
git commit -m "feat(api): add new endpoint"

# Run local tests
pytest tests/ -v

# Run linting
flake8 src/
black --check src/
```

### 2. Local Review Before Tagging

Review all changes that will go into the release:

```bash
# View commit log since last tag
git log v1.0.0..HEAD --oneline

# View detailed diff since last tag
git diff v1.0.0..HEAD

# Review changes by file
git diff v1.0.0..HEAD -- src/

# Show changed files only
git diff v1.0.0..HEAD --name-only
```

### 3. Commit & Push (before tagging)

Ensure all changes are committed and pushed:

```bash
# Verify working tree is clean
git status

# Push commits to remote (must happen before tag creation)
git push origin develop
```

### 4. Create Tag (Triggers Workflow)

After local review is complete, create a semantic version tag:

```bash
# Create annotated tag with message (recommended)
git tag -a v1.1.0 -m "Release v1.1.0: New API endpoints"

# Or lightweight tag (for lightweight releases)
git tag v1.1.0

# Push tag to remote (TRIGGERS CI/CD WORKFLOW)
git push origin v1.1.0

# Verify tag was created
git tag -l v1.1.0 -n
```

### 5. GitHub Actions Workflow Executes

When tag is pushed:
1. **verify-tag-creation** - Validates tag format (must be v{major}.{minor}.{patch})
2. **build-and-test** - Runs tests and builds Docker image
3. **deploy-production** - Requires approval, then deploys

## Semantic Versioning Rules

Tags MUST follow semantic versioning format:

✅ Valid tags:
- `v1.0.0` - Production release
- `v1.0.0-beta` - Pre-release version
- `v1.0.0-rc.1` - Release candidate
- `v2.0.1` - Patch release

❌ Invalid tags (rejected by workflow):
- `v1.0` - Missing patch version
- `1.0.0` - Missing 'v' prefix
- `release-1.0.0` - Wrong format
- `v1.0.0.0` - Too many version parts

## Manual Review Checklist

Before creating a tag, verify:

- [ ] All tests pass locally: `pytest tests/ -v`
- [ ] Linting passes: `flake8 src/` and `black --check src/`
- [ ] Docker builds successfully: `docker build .`
- [ ] All changes are committed and pushed
- [ ] CHANGELOG.md is updated with new version
- [ ] README.md reflects any new features
- [ ] No debug code or temporary files in commits
- [ ] All documentation is updated
- [ ] Version numbers match everywhere (package.json, setup.py, etc.)

## Workflow Status Check

### View workflow in GitHub UI
1. Go to GitHub repository
2. Click **Actions** tab
3. Click the workflow run name
4. Review each job status:
   - **verify-tag-creation** - Tag format validation
   - **build-and-test** - Compilation and tests
   - **deploy-production** - Deployment (requires approval)

### View workflow via CLI
```bash
# List recent workflow runs
gh run list

# View specific workflow run
gh run view <run-id>

# Watch workflow in real-time
gh run watch <run-id>

# Check deployment approval status
gh run view <run-id> --log
```

## Deployment Approval

Production deployments require explicit approval:

1. GitHub Actions workflow waits at `deploy-production` job
2. Repository admins receive notification for approval
3. Click "Review deployments" in GitHub Actions UI
4. Select "production" environment
5. Click "Approve and deploy"

### Approvers Configuration

Approvers are configured in GitHub repository settings:

1. Go to Settings → Environments → production
2. Add required approvers (team leads, release managers)
3. Only these users can approve deployments

## Workflow Conditions

| Job | Trigger | Condition |
|-----|---------|-----------|
| verify-tag-creation | Tag created | Always runs |
| build-and-test | Tag created | Only if tag is valid semver |
| deploy-staging | workflow_dispatch input | Only if user selects "staging" |
| deploy-production | Tag created | Only if tag is valid semver + approval |

## Reverting a Tag

If you accidentally created a tag or need to redo:

```bash
# Delete local tag
git tag -d v1.1.0

# Delete remote tag
git push origin --delete v1.1.0

# Create new corrected tag
git tag -a v1.1.1 -m "Release v1.1.1"
git push origin v1.1.1
```

## CI/CD Pipeline Details

### Verify Tag Creation Job
```yaml
- Validates tag matches v{major}.{minor}.{patch} pattern
- Extracts tag name for downstream jobs
- Outputs: tag-name, is-valid-semver
```

### Build & Test Job
```yaml
- Runs pytest with coverage
- Builds Docker image with semantic tag
- Pushes image to GHCR (GitHub Container Registry)
- Outputs: image-tag, image-digest
```

### Deploy Production Job
```yaml
- Requires GitHub Actions environment approval
- Validates semver tag format
- Deploys image to production
- Runs health checks and smoke tests
- Creates release notes automatically
```

## Environment Variables

Deployments use environment-specific variables:

```bash
# Production environment variables
APP_ENV=production
LOG_LEVEL=info
ENABLE_MONITORING=true
```

Set these in GitHub repository settings under **Environments**.

## Troubleshooting

### Tag not triggering workflow
- **Problem**: Tag created but workflow doesn't run
- **Solution**: 
  - Verify tag format matches `v{major}.{minor}.{patch}`
  - Ensure tag is pushed: `git push origin v1.0.0`
  - Check GitHub Actions for error messages

### Workflow fails at build-and-test
- **Problem**: Docker build or tests fail
- **Solution**:
  - Review GitHub Actions logs
  - Run tests locally: `pytest tests/ -v`
  - Fix issues and create new tag

### Deployment approval stuck
- **Problem**: Workflow waits for approval but never completes
- **Solution**:
  - Verify your account has deployment approval permission
  - Check environment protection rules in repository settings
  - Contact repository administrator

### Invalid semver format error
- **Problem**: Tag rejected as invalid format
- **Solution**:
  - Use correct format: `v{major}.{minor}.{patch}`
  - Examples: `v1.0.0`, `v2.1.3`, `v0.1.0-beta`
  - Delete and recreate tag if needed

## Best Practices

1. **Always local review** - Never skip reviewing changes before tagging
2. **One tag per release** - Don't create multiple tags for same release
3. **Meaningful messages** - Use descriptive tag messages
4. **Keep tags clean** - Delete old/test tags from remote
5. **Coordinate releases** - Communicate with team before creating tags
6. **Document changes** - Update CHANGELOG before tagging
7. **Test in staging** - Use workflow_dispatch to test staging deployments
8. **Monitor deployments** - Watch GitHub Actions until deployment completes

## Related Documentation

- [MASTER_PROJECT_BLUEPRINT.md](../maintenance/MASTER_PROJECT_BLUEPRINT.md) - Project standards
- [ONBOARDING.md](./ONBOARDING.md) - Developer onboarding
- [CI Pipeline Documentation](.github/workflows/ci.yml) - Testing workflow

## Questions or Issues?

Contact the DevOps team or open an issue in the repository.
