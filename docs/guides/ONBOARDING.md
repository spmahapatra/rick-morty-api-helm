# Developer Onboarding Guide - Master Project Blueprint v1.0

## Table of Contents
1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Configuration](#configuration)
5. [Running Services](#running-services)
6. [Testing](#testing)
7. [Git Workflow](#git-workflow)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)
10. [Getting Help](#getting-help)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- Your favorite editor/IDE (VS Code, PyCharm, etc.)

### Setup (5 minutes)

```bash
# 1. Clone the repository
git clone <repository-url>
cd <project-name>

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your local settings

# 5. Start services
docker-compose up -d

# 6. Run the application
python app.py

# 7. Validate installation
curl http://localhost:8000/health
```

**Expected Output:**
```json
{"status": "healthy"}
```

---

## Project Structure

```
project/
├── README.md                 # Project overview
├── .env.example              # Configuration template
├── .gitignore                # Git ignore rules
├── .gitmessage               # Git commit template
│
├── app.py                    # Application entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
├── docker-compose.yml        # Service orchestration
│
├── src/                      # Application source code
│   ├── __init__.py
│   ├── cache/                # Caching logic
│   ├── database/             # Database access
│   ├── middleware/           # Request middleware
│   ├── observability/        # Logging & monitoring
│   └── resilience/           # Error handling
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data
│
├── docs/                     # Documentation (8 categories)
│   ├── README.md             # Docs index
│   ├── architecture/         # System design
│   ├── api/                  # API endpoints
│   ├── deployment/           # Deployment guide
│   ├── dev-notes/            # Research & notes (git-ignored)
│   ├── guides/               # How-to guides
│   ├── maintenance/          # Operations & maintenance
│   └── troubleshooting/      # Common issues
│
├── .github/
│   ├── workflows/            # CI/CD pipelines
│   │   ├── ci.yml            # Testing & linting
│   │   └── cd.yml            # Deployment
│   └── agents/               # Copilot agents
│       └── blueprint-code-agent.yaml
│
├── .kilo/                    # Kilo CLI configuration
│   ├── command/              # Custom commands
│   └── agent/                # Custom agents
│
└── scripts/                  # Utility scripts
```

### Directory Standards

| Directory | Purpose | Git-Tracked |
|-----------|---------|------------|
| `src/` | Application code | ✅ Yes |
| `tests/` | Test code | ✅ Yes |
| `docs/` | Documentation | ✅ Yes (except dev-notes/) |
| `docs/dev-notes/` | Research & personal notes | ❌ No |
| `.github/` | GitHub config | ✅ Yes |
| `.kilo/` | Kilo CLI config | ✅ Yes |

---

## Development Workflow

### 1. Understanding the Codebase

**Read these first:**
1. `README.md` - Project overview
2. `docs/architecture/README.md` - System design
3. `docs/guides/DEVELOPMENT.md` - Development guide
4. `config.py` - Configuration structure

**Key Concepts:**
- **Modular Architecture**: Code organized by function (cache, database, etc.)
- **Configuration Management**: Environment-driven config via `config.py`
- **Structured Logging**: JSON-formatted logs for traceability
- **Error Handling**: Custom exceptions for domain errors
- **Docker-First**: All services containerized and orchestrated

### 2. Code Navigation

**Finding Things:**
```bash
# Find all imports of a module
grep -r "from src.cache import" .

# Find function definitions
grep -r "def get_user" src/

# Find error handling
grep -r "raise " src/resilience/

# Find logging calls
grep -r "logger\." src/
```

**Key Files to Understand:**
- `src/observability/logger.py` - Logging factory
- `src/resilience/exceptions.py` - Exception hierarchy
- `src/cache/detection.py` - Cache detection logic
- `config.py` - Configuration classes

### 3. Making Changes

**Typical Workflow:**
```bash
# 1. Create a feature branch
git checkout -b feature/add-user-cache

# 2. Make your changes
# Edit files, add tests

# 3. Run tests
pytest

# 4. Check code quality
black . && flake8 src && mypy src

# 5. Commit with Conventional Commits
git add .
git commit -m "feat(cache): add user cache with TTL support"

# 6. Push and create PR
git push origin feature/add-user-cache
```

---

## Configuration

### Environment Variables

All configuration comes from environment variables or `.env` file:

```bash
# Application
APP_ENV=development          # development, testing, production
APP_DEBUG=true               # Enable debug mode
APP_LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Server
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
DATABASE_POOL_SIZE=10

# Cache
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Using Configuration in Code

```python
from config import config

# Access configuration
print(config.API_PORT)        # 8000
print(config.APP_ENV)         # development
print(config.DATABASE_URL)    # Connection string

# Check environment
if config.APP_ENV == "production":
    # Production-specific logic
    pass
```

### Different Environments

```bash
# Development (default)
APP_ENV=development python app.py

# Testing
APP_ENV=testing pytest

# Production
APP_ENV=production python app.py
```

---

## Running Services

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app      # Follow app logs
docker-compose logs redis       # Redis logs only

# Stop services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check database
docker-compose exec postgres pg_isready -U postgres

# Check Redis
docker-compose exec redis redis-cli ping
```

### Service Details

| Service | Port | Health Check | Details |
|---------|------|--------------|---------|
| app | 8000 | GET /health | FastAPI application |
| postgres | 5432 | pg_isready | PostgreSQL database |
| redis | 6379 | PING | Redis cache |

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_cache.py

# Run specific test
pytest tests/unit/test_cache.py::test_cache_hit

# Run with coverage
pytest --cov=src --cov-report=html

# Run in verbose mode
pytest -v

# Run with markers
pytest -m "not slow"
```

### Test Structure

```
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_cache.py
│   ├── test_database.py
│   └── conftest.py       # Fixtures
│
├── integration/          # Tests with services
│   ├── test_api.py
│   └── conftest.py
│
└── fixtures/             # Test data
    ├── users.json
    └── responses.json
```

### Writing Tests

**Minimal Example:**
```python
import pytest
from src.cache.detection import detect_cache_hit

def test_cache_hit_detection():
    """Test cache hit detection logic."""
    result = detect_cache_hit(cache_response=True)
    assert result is True

def test_cache_miss_detection():
    """Test cache miss detection logic."""
    result = detect_cache_hit(cache_response=False)
    assert result is False
```

**With Fixtures:**
```python
@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    return MockRedis()

def test_cache_operations(mock_redis):
    """Test cache operations with mock."""
    mock_redis.set("key", "value")
    assert mock_redis.get("key") == "value"
```

### Coverage Requirements

- Minimum: 80% code coverage
- Targets: Core logic 90%+, utilities 70%+
- Run: `pytest --cov=src --cov-report=html`

---

## Git Workflow

### Branch Naming

Follow Git Flow naming conventions:

```
feature/description          # New features
fix/description              # Bug fixes
docs/description             # Documentation
refactor/description         # Code restructuring
perf/description             # Performance improvements
test/description             # Test additions
chore/description            # Maintenance tasks
```

### Commit Messages (Conventional Commits)

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**
```
feat(cache): add redis-backed caching layer
fix(database): correct connection pool recycling
docs(api): add endpoint documentation
refactor(logging): restructure logger hierarchy
test(cache): add cache hit detection tests
chore: update dependencies
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, etc.)
- `refactor` - Code restructuring
- `perf` - Performance improvements
- `test` - Test additions/modifications
- `chore` - Maintenance, dependencies
- `ci` - CI/CD configuration
- `security` - Security improvements

### Pull Request Process

1. **Create Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   ```bash
   # Edit files
   # Run tests
   pytest
   # Format code
   black .
   isort .
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(module): description"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/my-feature
   # Go to GitHub and create PR
   ```

5. **Address Reviews**
   - Read feedback
   - Make requested changes
   - Push again (commit is added automatically)

6. **Merge**
   - PR is merged by maintainer
   - Your feature branch is deleted

---

## Common Tasks

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/add-user-caching

# 2. Create module in src/
mkdir -p src/users
touch src/users/__init__.py
touch src/users/models.py
touch src/users/service.py

# 3. Write code with tests
# src/users/service.py - implementation
# tests/unit/test_users.py - tests

# 4. Test locally
pytest tests/unit/test_users.py
docker-compose up -d
python app.py

# 5. Commit and push
git add .
git commit -m "feat(users): add user caching service"
git push origin feature/add-user-caching
```

### Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b fix/cache-invalidation-bug

# 2. Write failing test first
# tests/unit/test_cache_bug.py

# 3. Fix the code
# src/cache/detection.py

# 4. Verify test passes
pytest tests/unit/test_cache_bug.py

# 5. Commit and push
git add .
git commit -m "fix(cache): correct invalidation logic"
git push origin fix/cache-invalidation-bug
```

### Adding Documentation

```bash
# 1. Create branch
git checkout -b docs/add-caching-guide

# 2. Add documentation
# docs/guides/CACHING.md

# 3. Update docs index
# docs/README.md - add reference

# 4. Commit
git add docs/
git commit -m "docs: add caching architecture guide"
git push origin docs/add-caching-guide
```

### Running Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 src tests

# Type check
mypy src

# All at once
black . && isort . && flake8 src tests && mypy src
```

### Updating Dependencies

```bash
# Add new dependency
pip install package-name
pip freeze > requirements.txt

# Update all dependencies
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Commit
git add requirements.txt
git commit -m "chore: update dependencies"
```

---

## Troubleshooting

### Common Issues

#### Issue: Docker services won't start
```bash
# Check logs
docker-compose logs postgres
docker-compose logs redis

# Clean up and restart
docker-compose down -v
docker-compose up -d

# Check health
docker-compose ps
```

#### Issue: Python import errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue: Database connection failed
```bash
# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Wait for database to be ready
docker-compose logs postgres
# Watch for "database system is ready to accept connections"

# Test connection
python -c "from config import config; print(config.DATABASE_URL)"
```

#### Issue: Tests failing locally but passing in CI
```bash
# Ensure you're using the same Python version
python --version  # Should be 3.11+

# Run tests same way as CI
pytest --cov=src --cov-report=xml

# Check for environment variables
printenv | grep APP_

# Clear pytest cache
rm -rf .pytest_cache
pytest
```

#### Issue: Git commit template not showing
```bash
# Ensure .gitmessage exists
cat .gitmessage

# Configure git
git config commit.template .gitmessage

# Verify
git config commit.template
```

### Getting Logs

```bash
# Application logs
docker-compose logs app

# Follow in real-time
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# Database logs
docker-compose logs postgres

# All services
docker-compose logs
```

### Useful Commands

```bash
# List all running services
docker-compose ps

# Execute command in container
docker-compose exec app python script.py

# Rebuild images
docker-compose build --no-cache

# Remove everything
docker-compose down -v --remove-orphans

# Check resource usage
docker stats
```

---

## Getting Help

### Documentation
- **Project Overview**: Read `README.md`
- **Architecture**: See `docs/architecture/README.md`
- **API Docs**: Check `docs/api/README.md`
- **Deployment**: Review `docs/deployment/README.md`
- **Troubleshooting**: Look in `docs/troubleshooting/README.md`

### Internal Resources
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Python PEP 8**: https://pep8.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Getting Support

1. **Check Existing Issues**: Search GitHub issues
2. **Check Documentation**: Review docs folder
3. **Ask in Slack/Teams**: Reach out to the team
4. **Create an Issue**: If problem persists
5. **Contact Maintainer**: For critical issues

### Common Questions

**Q: How do I add a new environment variable?**
A: Add to `.env.example`, update `config.py`, document in README.md

**Q: How do I run a specific test?**
A: `pytest tests/unit/test_cache.py::test_function_name`

**Q: How do I format my code?**
A: Run `black .` to auto-format, then `pytest` to verify

**Q: Can I commit without a test?**
A: Not recommended. Write tests first, then code.

**Q: How do I revert a commit?**
A: `git revert <commit-hash>` (safe) or `git reset --hard <commit-hash>` (destructive)

---

## Summary

**Key Takeaways:**
1. ✅ Use virtual environment: `source venv/bin/activate`
2. ✅ Configure .env before running
3. ✅ Always write tests before code
4. ✅ Use Conventional Commits format
5. ✅ Run `pytest` before pushing
6. ✅ Follow code style with `black` and `flake8`
7. ✅ Keep documentation updated
8. ✅ Use Docker for services

**Next Steps:**
1. Set up your environment (follow Quick Start)
2. Read the architecture docs
3. Make a small documentation change to practice the workflow
4. Ask questions early and often

Welcome to the team! 🚀

