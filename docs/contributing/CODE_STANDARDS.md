# Code Standards and Best Practices

## Overview

This document defines code standards, naming conventions, and best practices for the Rick and Morty API project.

## Python Style Guide

### Language Versions
- **Minimum**: Python 3.9
- **Target**: Python 3.11+
- **Type Hints**: Required on public functions

### Formatting

**Use Black** for automatic code formatting:

```bash
black src/ tests/ app.py config.py
```

Configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py39']
```

### Linting

**Use Flake8** for style violations:

```bash
flake8 src/ tests/ --max-line-length=100
```

Configuration in `.flake8`:
```ini
[flake8]
max-line-length = 100
exclude = __pycache__,venv
ignore = E203,W503
```

### Type Checking

**Use MyPy** for static type analysis:

```bash
mypy src/ app.py config.py
```

Configuration in `mypy.ini`:
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## Naming Conventions

### Variables and Functions
```python
# Good
cache_key = "character:1"
def get_character_by_id(char_id: int) -> Character:
    pass

# Bad
cacheKey = "character:1"
def getCharacterById(charId):
    pass
```

### Classes
```python
# Good
class CacheBackend:
    pass

class PostgresConnection:
    pass

# Bad
class cache_backend:
    pass

class postgres_connection:
    pass
```

### Constants
```python
# Good
CACHE_TTL = 3600
DEFAULT_LOG_LEVEL = "INFO"
MAX_RETRIES = 3

# Bad
cache_ttl = 3600
defaultLogLevel = "INFO"
max_retries = 3
```

### Private Methods and Variables
```python
class Service:
    def __init__(self):
        self._internal_state = None  # Private
        
    def _private_method(self) -> None:  # Private method
        pass
    
    def public_method(self) -> None:  # Public method
        pass
```

## Code Organization

### File Structure

```python
# Imports organized in groups (standard, third-party, local)
import logging
from typing import Optional, Dict

import requests
from flask import Flask

from src.cache.backend import CacheBackend
from src.db.models import Character

# Constants after imports
DEFAULT_TIMEOUT = 30
CACHE_TTL = 3600

# Classes and functions
class MyClass:
    pass

def my_function() -> str:
    pass
```

### Module Organization
- **Top**: Docstring explaining module purpose
- **Imports**: Organized as above
- **Constants**: Module-level configuration
- **Classes**: Main implementations
- **Functions**: Utility functions
- **__all__**: Export list for "from module import *"

Example:
```python
"""Database connection and pool management."""

import logging
from typing import Optional

import psycopg2

logger = logging.getLogger(__name__)

DEFAULT_POOL_SIZE = 10

class ConnectionPool:
    """Manage database connections."""
    pass

def get_connection() -> psycopg2.connection:
    """Get a connection from the pool."""
    pass

__all__ = ['ConnectionPool', 'get_connection']
```

## Documentation Standards

### Module Docstrings
```python
"""Module purpose and description.

This module handles X functionality, providing Y capabilities
for Z use case.

Key classes:
    ClassName: Brief description
    
Key functions:
    function_name: Brief description
"""
```

### Function and Method Docstrings
```python
def get_character(char_id: int) -> Character:
    """Retrieve character by ID.
    
    Fetches character data from cache if available,
    otherwise calls external API and caches result.
    
    Args:
        char_id: Unique character identifier (1-600)
        
    Returns:
        Character object with all available fields
        
    Raises:
        ValueError: If char_id is invalid (≤0 or >600)
        RequestError: If external API is unreachable
        CacheError: If cache backend fails
        
    Examples:
        >>> character = get_character(1)
        >>> print(character.name)
        'Rick Sanchez'
    """
    pass
```

### Class Docstrings
```python
class CacheBackend:
    """Redis-based caching system.
    
    Provides high-performance in-memory caching with
    automatic TTL expiration and stats tracking.
    
    Attributes:
        redis_url: Connection string for Redis server
        ttl: Time-to-live in seconds
        
    Example:
        >>> cache = CacheBackend('redis://localhost:6379')
        >>> cache.set('key', value, ttl=3600)
        >>> data = cache.get('key')
    """
    pass
```

### Complex Logic Comments
```python
# Good - explains WHY
if cache_hit and time.time() - cache_time > TTL:
    # Cache entry expired based on custom TTL logic
    # (Redis TTL not reliable for this case)
    cache_entry = None

# Bad - explains WHAT (code already shows this)
if cache_hit and time.time() - cache_time > TTL:
    # Clear cache entry
    cache_entry = None
```

## Code Structure Best Practices

### Error Handling

```python
# Good - specific exceptions
from src.utils.errors import CacheError, DatabaseError

try:
    data = cache.get(key)
except CacheError as e:
    logger.error("Cache operation failed", extra={"error": str(e)})
    raise
except Exception as e:
    logger.error("Unexpected error", extra={"error": str(e)})
    raise

# Bad - generic exception catching
try:
    data = cache.get(key)
except:
    pass  # Swallows all exceptions
```

### Logging

```python
# Good - structured logging
logger.info(
    "Character retrieved",
    extra={
        "character_id": char_id,
        "cache_hit": cache_hit,
        "response_time_ms": response_time
    }
)

# Bad - unstructured logging
logger.info(f"Got character {char_id}")
```

### Type Hints

```python
# Good - complete type hints
from typing import Optional, List, Dict

def search_characters(
    name: str,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, any]:
    """Search characters by name."""
    pass

# Bad - no type hints
def search_characters(name, limit=10, offset=0):
    """Search characters by name."""
    pass
```

### Function Length

- **Ideal**: 20-50 lines
- **Maximum**: 100 lines (very rare exceptions)
- **Signs of too long**: Multiple responsibilities, hard to understand, lots of nesting

### Cyclomatic Complexity

Keep functions simple:
```python
# Bad - 6 nested conditions
if condition1:
    if condition2:
        if condition3:
            if condition4:
                if condition5:
                    do_something()

# Good - guard clauses
if not condition1:
    return
if not condition2:
    return
if not condition3:
    return
do_something()
```

## Testing Standards

### Test File Organization
```python
# tests/test_feature.py

import pytest
from unittest.mock import Mock, patch

from src.feature import MyClass

# Test class grouping related tests
class TestMyClass:
    """Test MyClass functionality."""
    
    @pytest.fixture
    def instance(self):
        """Provide test instance."""
        return MyClass()
    
    def test_successful_operation(self, instance):
        """Test happy path."""
        result = instance.do_something()
        assert result is not None
    
    def test_error_handling(self, instance):
        """Test error conditions."""
        with pytest.raises(ValueError):
            instance.invalid_operation()
    
    @patch('src.feature.external_api')
    def test_with_mock(self, mock_api, instance):
        """Test with mocked dependencies."""
        mock_api.return_value = {"data": "value"}
        result = instance.fetch_data()
        assert result == {"data": "value"}
```

### Test Naming

```python
# Good - clear about what is tested
def test_get_character_returns_correct_data():
    pass

def test_get_character_raises_on_invalid_id():
    pass

def test_cache_hit_returns_faster():
    pass

# Bad - unclear
def test_character():
    pass

def test_it_works():
    pass
```

### Assertions

```python
# Good - specific assertions
assert response.status_code == 200
assert response.json['status'] == 'success'
assert len(results) == 42

# Bad - vague assertions
assert response
assert results
```

## Security Best Practices

### Secrets Management
```python
# Good - use environment variables
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not set")

# Bad - hardcoded secrets
database_url = "postgresql://admin:password@localhost:5432/db"
```

### Input Validation
```python
# Good - validate all inputs
from src.utils.validators import validate_character_id

def get_character(char_id: int) -> Character:
    if not validate_character_id(char_id):
        raise ValueError(f"Invalid character ID: {char_id}")
    # ... rest of function

# Bad - no validation
def get_character(char_id):
    return query(f"SELECT * FROM characters WHERE id = {char_id}")
```

### Database Queries
```python
# Good - parameterized queries (via SQLAlchemy)
character = db.session.query(Character).filter(
    Character.id == char_id
).first()

# Bad - string concatenation (SQL injection!)
character = db.session.query(Character).filter(
    f"id = {char_id}"
).first()
```

### Error Messages
```python
# Good - safe error messages
except DatabaseError as e:
    logger.error("Database operation failed")
    return {"error": "Unable to process request"}, 500

# Bad - exposes sensitive info
except DatabaseError as e:
    return {"error": f"Database connection failed: {str(e)}"}, 500
```

## Performance Considerations

### Caching
- Cache database queries that don't change frequently
- Use appropriate TTL values (not too short, not too long)
- Monitor cache hit rates: `docs/guides/CACHE_HIT_MISS_DETECTION_GUIDE.md`

### Database
- Use indexes on frequently queried columns
- Limit query results with pagination
- Avoid N+1 queries with joins/eager loading

### Logging
- Don't log in tight loops
- Use appropriate log levels (not everything is INFO)
- Avoid logging large objects

## Import Organization

```python
# Standard library (alphabetical)
import json
import logging
import os
from typing import Dict, List, Optional

# Third-party libraries (alphabetical)
import psycopg2
import requests
from flask import Flask, jsonify
from redis import Redis

# Local imports (alphabetical)
from src.cache.backend import CacheBackend
from src.db.connection import get_connection
from src.logging.config import setup_logging
from src.utils.errors import CacheError

__all__ = ['MyClass', 'my_function']
```

## Configuration Management

```python
# Good - centralized in config.py
class Config:
    """Base configuration."""
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Override with production values

# Bad - scattered throughout codebase
CACHE_TTL = 3600  # in cache.py
LOG_LEVEL = "INFO"  # in logging.py
DEBUG = True  # in app.py
```

## Checklist Before Committing

- [ ] Code follows Black formatting
- [ ] No Flake8 warnings: `flake8 src/`
- [ ] Type hints pass MyPy: `mypy src/`
- [ ] Tests pass: `pytest`
- [ ] Tests cover new code (≥80% coverage)
- [ ] No secrets or passwords in code
- [ ] No debugging code (pdb, print, console.log)
- [ ] Documentation updated
- [ ] Commit message follows guidelines (see `docs/contributing/CONTRIBUTING.md`)

## Questions?

See related documentation:
- Development setup: `docs/contributing/DEVELOPMENT_SETUP.md`
- Contributing guide: `docs/contributing/CONTRIBUTING.md`
- Testing guide: `docs/contributing/TESTING_GUIDE.md`
