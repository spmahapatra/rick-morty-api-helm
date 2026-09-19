#!/bin/bash
# docker_build_validation.sh
# 
# This script performs comprehensive validation of the Docker build
# before allowing the application to fully start.
#
# It is invoked during Docker build as a pre-flight check.
# Must complete before gunicorn starts.

set -e

PROJECT_DIR="."
VALIDATION_LOG="$PROJECT_DIR/docker_build_validation.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Docker Build Validation Protocol"
echo "========================================="
echo ""

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$VALIDATION_LOG"
}

# Validation functions
validate_python_imports() {
    log "Validating Python imports..."
    
    python3 -c "
import sys
required_modules = [
    'flask',
    'flask_cors',
    'requests',
    'redis',
    'psycopg2',
    'sqlalchemy',
    'dotenv'
]

missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f'  ✓ {module}')
    except ImportError as e:
        print(f'  ✗ {module}: {e}')
        missing.append(module)

if missing:
    print(f'\nMissing modules: {missing}', file=sys.stderr)
    sys.exit(1)
" || {
        echo -e "${RED}✗ Python imports validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ All required Python modules available${NC}"
}

validate_application_imports() {
    log "Validating application imports..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    # Test importing app
    print('Importing app.py...')
    from app import app, cache_backend, cache_middleware
    print('  ✓ app.py imported successfully')
    
    # Test cache backend
    print(f'Cache backend type: {type(cache_backend).__name__}')
    print(f'Cache backend available: {cache_backend is not None}')
    
    # Test middleware
    print(f'Cache middleware available: {cache_middleware is not None}')
    
    print('Application imports: OK')
except Exception as e:
    print(f'Application import failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        echo -e "${RED}✗ Application import validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Application imports valid${NC}"
}

validate_database_schema() {
    log "Validating database schema..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from scripts.init_db import validate_database_url, init_database
    import os
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://admin:password@postgres:5432/rickmorty')
    
    print(f'Database URL: {db_url}')
    
    # Validate URL format
    validate_database_url(db_url)
    print('  ✓ Database URL format valid')
    
    # Initialize database
    init_database()
    print('  ✓ Database initialization complete')
    print('Database schema validation: OK')
    
except Exception as e:
    print(f'Database validation failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        echo -e "${RED}✗ Database schema validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Database schema validated${NC}"
}

validate_endpoints() {
    log "Validating Flask endpoints..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app import app
    
    # Expected endpoints
    expected_endpoints = {
        '/': 'root',
        '/health': 'health_check',
        '/characters': 'get_characters',
        '/characters/': 'get_characters',
        '/characters/<int:character_id>': 'get_character_by_id',
        '/api/cache/stats': 'get_cache_stats',
        '/api/cache/flush': 'flush_cache',
        '/api/cache/analytics': 'get_cache_analytics',
    }
    
    # Get all routes
    routes = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes[rule.rule] = rule.endpoint
    
    # Validate
    missing = []
    for route, endpoint in expected_endpoints.items():
        if route not in routes:
            missing.append(route)
        else:
            print(f'  ✓ {route}')
    
    if missing:
        print(f'Missing endpoints: {missing}', file=sys.stderr)
        sys.exit(1)
    
    print('Endpoint validation: OK')
    
except Exception as e:
    print(f'Endpoint validation failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        echo -e "${RED}✗ Endpoint validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ All endpoints registered${NC}"
}

validate_cache_backend() {
    log "Validating cache backend..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from config import get_cache_backend
    import json
    
    backend = get_cache_backend()
    backend_type = type(backend).__name__
    print(f'Cache backend: {backend_type}')
    
    # Try basic operations
    test_key = 'docker_validation_test'
    test_data = {'test': 'data', 'timestamp': 12345}
    
    # Store
    success = backend.set(test_key, test_data, ttl_seconds=60)
    if success:
        print('  ✓ Cache store operation successful')
    else:
        print('  ⚠ Cache store operation failed (fallback mode?)')
    
    # Retrieve
    retrieved = backend.get(test_key)
    if retrieved == test_data:
        print('  ✓ Cache retrieve operation successful')
    elif retrieved is None and backend_type == 'RedisBackend':
        print('  ✗ Cache retrieve returned None after store')
        sys.exit(1)
    else:
        print(f'  ⚠ Retrieved data differs: {retrieved}')
    
    # Get stats
    stats = backend.get_stats()
    print(f'  ✓ Cache stats: {json.dumps(stats, indent=2)}')
    
    # Clean up
    backend.delete(test_key)
    
    print('Cache backend validation: OK')
    
except Exception as e:
    print(f'Cache backend validation failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        echo -e "${RED}✗ Cache backend validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Cache backend validated${NC}"
}

validate_logging() {
    log "Validating structured logging..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from src.observability.logging import setup_logging, StructuredLogger
    
    # Check if logging is set up
    setup_logging(level='INFO', format_type='json')
    logger = StructuredLogger('validation')
    
    # Test logging
    logger.info('Test log message', test_field='value')
    
    print('  ✓ Logging initialized')
    print('  ✓ StructuredLogger available')
    print('Logging validation: OK')
    
except Exception as e:
    print(f'Logging validation failed: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
        echo -e "${RED}✗ Logging validation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Structured logging validated${NC}"
}

# Run all validations
echo ""
log "Starting Docker build validations..."
echo ""

validate_python_imports || exit 1
echo ""

validate_application_imports || exit 1
echo ""

validate_database_schema || exit 1
echo ""

validate_endpoints || exit 1
echo ""

validate_cache_backend || exit 1
echo ""

validate_logging || exit 1
echo ""

# Summary
log "========================================="
log "All Docker build validations PASSED"
log "========================================="
echo -e "${GREEN}✓ Application is ready for deployment${NC}"
echo ""

echo "Validation Summary:"
echo "  ✓ Python dependencies available"
echo "  ✓ Application code imports successfully"
echo "  ✓ Database connection and schema verified"
echo "  ✓ All endpoints registered"
echo "  ✓ Cache backend operational"
echo "  ✓ Structured logging configured"
echo ""
echo "Application will now start with gunicorn..."
echo ""
