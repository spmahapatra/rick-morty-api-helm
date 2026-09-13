# Contributing Guidelines

## Welcome!

We appreciate contributions to the Rick and Morty API project! This guide explains how to contribute effectively.

## Code of Conduct

- Be respectful and professional
- Provide constructive feedback
- Report issues responsibly
- Focus on improving the project

## Getting Started

1. **Fork the Repository**
   ```bash
   # On GitHub, click "Fork"
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/setupAppCreDepHelmPkg.git
   cd setupAppCreDepHelmPkg
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Follow Setup Guide**
   - See `docs/contributing/DEVELOPMENT_SETUP.md`

## Contribution Types

### Bug Reports
- **Where**: GitHub Issues
- **Include**:
  - Clear description of the bug
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (Python version, OS, etc.)
  - Relevant error logs

### Feature Requests
- **Where**: GitHub Discussions
- **Include**:
  - Clear description of the feature
  - Use case and motivation
  - Proposed API design (if applicable)
  - Any implementation considerations

### Code Contributions
1. **Create feature branch** (see Getting Started)
2. **Follow Code Standards** (see `docs/contributing/CODE_STANDARDS.md`)
3. **Write tests** for new functionality
4. **Update documentation** for API changes
5. **Run quality checks** before submitting
6. **Create Pull Request** with clear description

### Documentation

All documentation contributions must follow our organization standards.

#### Documentation File Organization

**ALL markdown documentation must be placed in `/docs` subdirectories** (except `README.md` in root).

```
docs/
├── api/              # API reference documentation
├── architecture/     # Architecture and design docs
├── contributing/     # Contribution guidelines
├── deployment/       # Deployment procedures
├── examples/         # Example configurations
├── guides/           # How-to guides and tutorials
├── maintenance/      # Maintenance and analysis
└── operations/       # Operational procedures
```

**Examples of correct locations:**

| File Purpose | Correct Location | Incorrect Location |
|---|---|---|
| CI/CD setup guide | `docs/guides/CI_CD_SETUP.md` | ❌ `CI_CD_SETUP.md` |
| Security analysis | `docs/maintenance/SECURITY_ANALYSIS.md` | ❌ `SECURITY_ANALYSIS.md` |
| Deployment checklist | `docs/deployment/DEPLOYMENT_CHECKLIST.md` | ❌ `DEPLOYMENT_CHECKLIST.md` |
| API reference | `docs/api/API_REFERENCE.md` | ❌ `API_REFERENCE.md` |

**Pre-commit hook enforcement:**

Before committing, a pre-commit hook will reject any markdown files in the root directory:

```bash
$ git commit -m "Add CI/CD guide"
❌ Error: Markdown files must be in /docs subdirectories
Files in root directory:
  - CI_CD_GUIDE.md

Move files to appropriate /docs subdirectories:
  - CI/CD guides → docs/guides/
```

**Fix:** Move files to appropriate `/docs` subdirectories before committing:

```bash
git mv CI_CD_GUIDE.md docs/guides/
git commit -m "docs: add CI/CD setup guide"
```

#### Documentation Contribution Types

- Fix typos and clarify explanations
- Add examples and tutorials
- Improve guides and references
- Update outdated information

## Development Workflow

### 1. Make Changes

```bash
# Edit files
# Run tests
pytest

# Check code quality
flake8 src/
mypy src/
black src/
```

### 2. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message (see Commit Guidelines)
git commit -m "feat: add new feature"

# View your commits
git log --oneline -5
```

### 3. Push to Fork

```bash
git push origin feature/your-feature-name
```

### 4. Create Pull Request

- **On GitHub**: Click "New Pull Request"
- **Base**: main
- **Compare**: your-feature-branch
- **Title**: Clear, concise description
- **Description**: Include:
  - What changes were made
  - Why the changes were needed
  - How to test the changes
  - Related issues (use #123 format)

### 5. Code Review

- Respond to reviewer feedback
- Make requested changes
- Request re-review when ready

### 6. Merge

- Maintainer will merge once approved
- Your branch will be deleted
- Changes appear in next release

## Commit Guidelines

### Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, missing semicolons)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Test additions or updates
- `chore`: Build, dependencies, configuration

### Scope
- `api`: Flask API changes
- `cache`: Caching system
- `db`: Database layer
- `logging`: Logging system
- `config`: Configuration
- `docs`: Documentation

### Subject
- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Max 50 characters

### Example
```
feat(cache): add cache statistics endpoint

Add new GET /cache/stats endpoint to retrieve:
- Total requests and hit/miss counts
- Hit rate percentage
- Average response times
- Current cache size

Fixes #123
```

## Testing Requirements

### Write Tests For
- New features
- Bug fixes
- API changes
- Database queries
- Cache operations

### Test Structure

```python
# tests/test_feature.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_new_endpoint(client):
    """Test description"""
    response = client.get('/endpoint')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

### Run Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_cache.py

# With coverage
pytest --cov=src

# Verbose
pytest -v
```

### Coverage Requirements
- New code should have ≥ 80% test coverage
- Run `pytest --cov=src` to check coverage

## Documentation Requirements

### Update Documentation When
- Adding new endpoints → `docs/api/API_REFERENCE.md`
- Changing configuration → `docs/architecture/ARCHITECTURE_OVERVIEW.md`
- Adding features → Create new guide in `docs/guides/`
- Changing deployment process → Update `docs/deployment/`

### Documentation Format

- Use clear, concise language
- Include code examples
- Provide links to related documentation
- Use headers to organize content
- Include tables for reference material

## Code Review Checklist

Before submitting a PR, ensure:
- [ ] Tests pass: `pytest`
- [ ] Code quality: `flake8`, `mypy`, `black`
- [ ] No secrets in code (passwords, keys, tokens)
- [ ] Docstrings on public functions
- [ ] Updated relevant documentation
- [ ] Commit messages follow guidelines
- [ ] Changes are focused (not mixing unrelated changes)
- [ ] No breaking API changes without discussion

## Release Process

Releases follow Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

See `docs/maintenance/CHANGELOG.md` for release notes.

## Dispute Resolution

If you disagree with a decision:
1. Discuss respectfully with maintainers
2. Provide technical reasoning
3. Accept maintainer's decision
4. Appeal to project steering committee (if applicable)

## Contact

- **Questions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Security Concerns**: security@example.com

## Thank You

Contributors are the heart of open source. Thank you for helping improve this project!
