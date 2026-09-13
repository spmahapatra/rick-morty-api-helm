# Quick Reference: Tag-Based Deployment

## Standard Release Workflow

```bash
# 1. Development and testing (local)
git add .
git commit -m "feat(api): add new endpoint"
pytest tests/ -v
black src/

# 2. Push commits to remote
git push origin develop

# 3. Review changes locally
./scripts/review-release.sh v1.0.0

# 4. Create and push tag (TRIGGERS CI/CD)
git tag -a v1.1.0 -m "Release v1.1.0: New features"
git push origin v1.1.0

# 5. Monitor in GitHub Actions
# Go to: https://github.com/spmahapatra/rick-morty-api-helm/actions
# Approve production deployment when prompted
```

## Commands Quick Reference

| Task | Command |
|------|---------|
| Run release review | `./scripts/review-release.sh v1.0.0` |
| View commits since tag | `git log v1.0.0..HEAD --oneline` |
| View diff since tag | `git diff v1.0.0..HEAD` |
| Create annotated tag | `git tag -a v1.1.0 -m "Release v1.1.0"` |
| Push tag to trigger workflow | `git push origin v1.1.0` |
| List all tags | `git tag -l` |
| Delete local tag | `git tag -d v1.1.0` |
| Delete remote tag | `git push origin --delete v1.1.0` |
| View tag message | `git show v1.1.0` |

## Tag Format Requirements

✅ **Valid format**: `v{major}.{minor}.{patch}`

Examples:
- `v1.0.0` - Production release
- `v1.0.1` - Patch release
- `v1.1.0` - Minor release
- `v2.0.0` - Major release
- `v1.0.0-beta` - Pre-release

❌ **Invalid** - Will be rejected:
- `v1.0` (missing patch)
- `1.0.0` (missing v prefix)
- `release-1.0.0` (wrong format)

## Workflow Status in GitHub

**Navigate to Actions tab:**
```
GitHub Repo → Actions → Latest Run → View Logs
```

**Jobs that run:**
1. `verify-tag-creation` - Validates tag format
2. `build-and-test` - Runs tests, builds Docker image
3. `deploy-production` - Requires approval, then deploys

## Stopping/Canceling Deployment

```bash
# Cancel running workflow (via CLI)
gh run cancel <run-id>

# View workflow runs
gh run list

# Watch workflow in real-time
gh run watch <run-id>
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tag didn't trigger workflow | Push tag: `git push origin v1.0.0` |
| Tests failing in workflow | Fix locally: `pytest tests/ -v` then new tag |
| Build failed | Check Docker: `docker build .` |
| Deployment stuck waiting | Check approval in GitHub Actions UI |
| Wrong tag created | Delete: `git push origin --delete v1.0.0` then retry |

## Environment Setup

Copy this to your shell profile (~/.bashrc or ~/.zshrc) for convenience:

```bash
# Release review function
alias release-review='./scripts/review-release.sh'

# Quick tag creation
function create-tag() {
    local tag="${1:-v1.0.0}"
    local msg="${2:-Release $tag}"
    git tag -a "$tag" -m "$msg" && git push origin "$tag"
}

# View workflow status
function view-actions() {
    gh run list --limit 5
}
```

## Full Documentation

See [TAG_BASED_DEPLOYMENT.md](TAG_BASED_DEPLOYMENT.md) for complete details.
