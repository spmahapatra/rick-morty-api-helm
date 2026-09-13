# Development Setup Guide

## Prerequisites

- **Python**: 3.9+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Make** (optional): For convenient command shortcuts

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd setupAppCreDepHelmPkg
```

### 2. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 4. Setup Environment Variables

Create a `.env` file in the project root:

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/rickmorty
DB_POOL_SIZE=10
DB_POOL_RECYCLE=3600

# Redis
REDIS_URL=redis://localhost:6379/0

# Cache
CACHE_TTL=3600
CACHE_BACKEND=redis

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# External API
RICK_MORTY_API_URL=https://rickandmortyapi.com/api
API_TIMEOUT=30
MAX_RETRIES=3
RETRY_BACKOFF=1.5

# Server
HOST=127.0.0.1
PORT=5000
WORKERS=1
```

### 5. Start Services with Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- API service on port 5000

### 6. Initialize Database Schema

```bash
python -m src.db.init
```

Or manually:

```bash
python3 << 'EOF'
from src.db.connection import get_connection
from src.db.schema import create_tables

conn = get_connection()
create_tables(conn)
conn.close()
print("Database initialized successfully!")
EOF
```

### 7. Run the API

```bash
python app.py
```

Or with Flask CLI:

```bash
flask run
```

The API will be available at `http://localhost:5000`

## Docker-Based Development

### Using Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Clean up volumes (careful!)
docker-compose down -v
```

### Running Tests in Docker

```bash
docker-compose exec api pytest tests/ -v
```

## Project Structure

```
setupAppCreDepHelmPkg/
├── app.py                          # Main Flask application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── docker-compose.yml              # Docker services composition
├── Dockerfile                      # API container image
├── .env                           # Environment variables (local)
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview (root)
│
├── src/                           # Application source code
│   ├── api/                       # External API integration
│   │   ├── __init__.py
│   │   ├── client.py             # HTTP client with retries
│   │   └── schema.py             # Response validation
│   │
│   ├── cache/                    # Caching system
│   │   ├── __init__.py
│   │   ├── backend.py            # Redis backend
│   │   ├── detection.py          # Hit/miss detection
│   │   └── middleware.py         # WSGI middleware
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py         # Pool management
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schema.py             # Table definitions
│   │   └── init.py              # Schema initialization
│   │
│   ├── logging/                  # Structured logging
│   │   ├── __init__.py
│   │   ├── config.py            # Logger setup
│   │   ├── formatters.py        # Custom formatters
│   │   └── context.py           # Correlation IDs
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── errors.py            # Custom exceptions
│       └── validators.py        # Input validation
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_api.py              # API endpoint tests
│   ├── test_cache.py            # Cache system tests
│   ├── test_db.py               # Database tests
│   └── test_integration.py      # Integration tests
│
├── docs/                         # Documentation (this directory)
│   ├── README.md
│   ├── guides/
│   ├── deployment/
│   ├── api/
│   ├── architecture/
│   ├── operations/
│   ├── contributing/
│   ├── maintenance/
│   ├── examples/
│   └── dev-notes/
│
└── scripts/                      # Utility scripts
    ├── docker_build_validation.sh
    ├── db_setup.sh
    └── health_check.sh
```

## Common Development Tasks

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_cache.py

# With coverage
pytest --cov=src tests/

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Code Quality Checks

```bash
# Linting
flake8 src/ tests/ app.py config.py

# Type checking
mypy src/ app.py config.py

# Code formatting
black src/ tests/ app.py config.py

# Security scanning
bandit -r src/
```

### Database Operations

```bash
# Connect to PostgreSQL
psql postgresql://admin:password@localhost:5432/rickmorty

# View tables
\dt

# View table schema
\d characters

# Exit
\q
```

### Redis Operations

```bash
# Connect to Redis CLI
redis-cli -n 0

# View all keys
KEYS *

# View cache stats
INFO stats

# Flush all data
FLUSHALL

# Exit
exit
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test character retrieval
curl http://localhost:5000/characters/1

# Test character search
curl 'http://localhost:5000/characters/search?name=rick'

# Test cache flush
curl -X POST http://localhost:5000/cache/flush

# Test cache stats
curl http://localhost:5000/cache/stats
```

## Debugging

### Enable Debug Logging

Set `FLASK_DEBUG=1` and `LOG_LEVEL=DEBUG` in `.env`:

```bash
FLASK_DEBUG=1
LOG_LEVEL=DEBUG
```

### Using Python Debugger

```python
import pdb; pdb.set_trace()  # Place in code for breakpoint
```

Or with VS Code: Add `.vscode/launch.json` configuration for remote debugging.

### View Application Logs

```bash
# Container logs
docker-compose logs -f api

# Follow Flask logs
flask run --with-threads

# Structured logs (JSON)
docker-compose logs api | jq '.'
```

### Database Query Logging

Enable in `config.py`:

```python
SQLALCHEMY_ECHO = True  # Log all SQL queries
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Verify connection string
psql "postgresql://admin:password@localhost:5432/rickmorty"
```

### Redis Connection Errors

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
redis-cli ping

# View Redis logs
docker-compose logs redis
```

### Cache Not Working

- Check REDIS_URL in `.env`
- Verify Redis is running: `redis-cli ping`
- Check cache logs: `docker-compose logs api | grep cache`
- Flush and restart: `curl -X POST http://localhost:5000/cache/flush`

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: describe your changes"

# Push to remote
git push origin feature/your-feature

# Create Pull Request
# Review and merge via GitHub

# Update local main
git checkout main
git pull origin main
```

See `docs/contributing/GIT_WORKFLOW.md` for detailed Git guidelines.

## Next Steps

1. Review `docs/api/API_REFERENCE.md` to understand available endpoints
2. Read `docs/guides/CACHE_HIT_MISS_DETECTION_GUIDE.md` for cache behavior
3. Check `docs/contributing/CODE_STANDARDS.md` for coding guidelines
4. Explore `docs/examples/` for usage examples
