#!/usr/bin/env python3
"""
PRE-DOCKER BUILD VALIDATION TEST SUITE


This test suite validates all critical application functionality
before Docker containerization to prevent wasted build cycles.

Run this LOCALLY before any Docker build command.

Usage:
  python3 pre_docker_test.py
"""

import sys
import json
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_pass(text):
    """Print pass message"""
    print(f"{Colors.GREEN}✓ PASS:{Colors.END} {text}")


def print_fail(text):
    """Print fail message"""
    print(f"{Colors.RED}✗ FAIL:{Colors.END} {text}")


def print_warn(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ WARN:{Colors.END} {text}")


# ============================================================================
# TEST 1: Cache Backend Storage and Retrieval
# ============================================================================

def test_cache_backend_storage():
    """Test that cache backend can store and retrieve data"""
    print_header("TEST 1: Cache Backend Storage & Retrieval")
    
    try:
        # Test Redis backend
        logger.info("Attempting Redis connection...")
        from src.cache.backend import RedisBackend
        
        redis_backend = RedisBackend(
            url="redis://localhost:6379/0",
            pool_size=5,
            socket_timeout=2
        )
        
        if not redis_backend.client:
            print_warn("Redis not available - will test InMemory backend")
            
            from src.cache.backend import InMemoryBackend
            backend = InMemoryBackend()
            backend_type = "InMemory"
        else:
            backend = redis_backend
            backend_type = "Redis"
            
        # Test 1.1: Basic set/get
        test_key = "test:cache:key"
        test_data = {"status": "success", "data": [1, 2, 3]}
        
        logger.info(f"Testing {backend_type} backend...")
        
        # Clear first
        backend.delete(test_key)
        
        # Store data
        success = backend.set(test_key, test_data, ttl_seconds=60)
        if not success:
            print_fail(f"Failed to store data in {backend_type} backend")
            return False
        print_pass(f"Successfully stored data in {backend_type} backend")
        
        # Retrieve data
        retrieved = backend.get(test_key)
        if retrieved is None:
            print_fail(f"Failed to retrieve data from {backend_type} backend")
            return False
        print_pass(f"Successfully retrieved data from {backend_type} backend")
        
        # Verify data integrity
        if retrieved != test_data:
            print_fail(f"Retrieved data doesn't match stored data")
            logger.error(f"Expected: {test_data}")
            logger.error(f"Got: {retrieved}")
            return False
        print_pass(f"Data integrity verified")
        
        # Test 1.2: TTL expiration
        logger.info("Testing TTL expiration...")
        backend.set("ttl_test", {"data": "expires"}, ttl_seconds=1)
        
        result_before = backend.get("ttl_test")
        if result_before is None:
            print_fail("Data expired too quickly (TTL test)")
            return False
        print_pass("Data available before TTL expiration")
        
        # For InMemory backend, we can test expiration
        if backend_type == "InMemory":
            time.sleep(1.2)
            result_after = backend.get("ttl_test")
            if result_after is not None:
                print_fail("Data not expired after TTL (TTL test)")
                return False
            print_pass("Data correctly expired after TTL")
        else:
            print_warn("Skipping TTL expiration test for Redis (would require waiting)")
        
        # Test 1.3: Statistics
        logger.info("Testing statistics tracking...")
        stats = backend.get_stats()
        if "hits" not in stats or "misses" not in stats:
            print_fail("Statistics not properly tracked")
            return False
        print_pass(f"Statistics properly tracked: {stats}")
        
        print_pass(f"All cache backend tests passed with {backend_type}")
        return True
        
    except ImportError as e:
        print_fail(f"Import error: {e}")
        return False
    except Exception as e:
        print_fail(f"Exception during cache backend test: {type(e).__name__}: {e}")
        return False


# ============================================================================
# TEST 2: Database Connection & Schema
# ============================================================================

def test_database_connection():
    """Test database connection and schema"""
    print_header("TEST 2: Database Connection & Schema")
    
    try:
        from init_db import validate_database_url, init_database
        import os
        
        db_url = os.getenv('DATABASE_URL', 'postgresql://admin:password@localhost:5432/rickmorty')
        logger.info(f"Testing database at: {db_url}")
        
        # Test 2.1: URL validation
        try:
            validate_database_url(db_url)
            print_pass("Database URL validation passed")
        except Exception as e:
            print_fail(f"Database URL validation failed: {e}")
            return False
        
        # Test 2.2: Connection attempt (with retry)
        try:
            logger.info("Attempting database connection...")
            init_database()
            print_pass("Database connection successful")
        except Exception as e:
            print_fail(f"Database connection failed: {e}")
            return False
        
        # Test 2.3: Schema verification
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                # Check required tables
                required_tables = {"characters", "api_calls", "audit_logs", "cache_metadata"}
                
                result = conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                existing_tables = {row[0] for row in result.fetchall()}
                
                missing = required_tables - existing_tables
                if missing:
                    print_fail(f"Missing tables: {missing}")
                    return False
                print_pass(f"All required tables exist: {required_tables}")
        except Exception as e:
            print_fail(f"Schema verification failed: {e}")
            return False
        
        print_pass("All database tests passed")
        return True
        
    except ImportError as e:
        print_fail(f"Import error: {e}")
        return False
    except Exception as e:
        print_fail(f"Exception during database test: {type(e).__name__}: {e}")
        return False


# ============================================================================
# TEST 3: Flask Application Initialization
# ============================================================================

def test_flask_app_initialization():
    """Test Flask app can be initialized without errors"""
    print_header("TEST 3: Flask Application Initialization")
    
    try:
        logger.info("Importing Flask app...")
        from app import app, cache_backend, cache_middleware
        
        print_pass("App imported successfully")
        
        # Test 3.1: App context
        with app.app_context():
            print_pass("App context created successfully")
            
            # Test 3.2: Cache backend initialized
            if cache_backend is None:
                print_fail("Cache backend is None")
                return False
            print_pass(f"Cache backend initialized: {cache_backend}")
            
            # Test 3.3: Middleware initialized
            if cache_middleware is None:
                print_fail("Cache middleware is None")
                return False
            print_pass("Cache middleware initialized")
        
        print_pass("All Flask app initialization tests passed")
        return True
        
    except Exception as e:
        print_fail(f"Exception during app initialization: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 4: Endpoint Routing
# ============================================================================

def test_endpoint_routing():
    """Test that all endpoints are properly registered"""
    print_header("TEST 4: Endpoint Routing")
    
    try:
        from app import app
        
        # Get all routes
        routes = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes[rule.rule] = rule.endpoint
        
        # Expected routes
        expected_routes = {
            '/': 'root',
            '/health': 'health_check',
            '/characters': 'get_characters',
            '/characters/': 'get_characters',
            '/characters/<int:character_id>': 'get_character_by_id',
            '/api/cache/stats': 'get_cache_stats',
            '/api/cache/flush': 'flush_cache',
            '/api/cache/analytics': 'get_cache_analytics',
        }
        
        logger.info("Registered routes:")
        for route in sorted(routes.keys()):
            logger.info(f"  {route} -> {routes[route]}")
        
        # Check required routes
        missing_routes = []
        for route, endpoint in expected_routes.items():
            if route not in routes:
                missing_routes.append(route)
            elif routes[route] != endpoint:
                print_warn(f"Route {route} has endpoint {routes[route]}, expected {endpoint}")
        
        if missing_routes:
            print_fail(f"Missing routes: {missing_routes}")
            return False
        
        print_pass(f"All expected routes registered ({len(expected_routes)} routes)")
        return True
        
    except Exception as e:
        print_fail(f"Exception during routing test: {type(e).__name__}: {e}")
        return False


# ============================================================================
# TEST 5: Middleware Functionality
# ============================================================================

def test_middleware_functionality():
    """Test that middleware is working correctly"""
    print_header("TEST 5: Middleware Functionality")
    
    try:
        from app import app
        from flask import g
        
        logger.info("Testing request/response cycle...")
        
        with app.test_client() as client:
            # Test 5.1: Health check (bypassed from cache)
            logger.info("Testing /health endpoint...")
            response = client.get('/health')
            
            if response.status_code != 200:
                print_fail(f"Health check failed: {response.status_code}")
                return False
            print_pass(f"Health check OK (status: {response.status_code})")
            
            # Check for cache headers
            if 'X-Cache' not in response.headers:
                print_fail("Missing X-Cache header")
                return False
            print_pass(f"X-Cache header present: {response.headers['X-Cache']}")
            
            # Test 5.2: Characters endpoint (should be cached)
            logger.info("Testing /characters endpoint (first request)...")
            response1 = client.get('/characters')
            
            if response1.status_code != 200:
                print_fail(f"Characters endpoint failed: {response1.status_code}")
                logger.error(f"Response: {response1.get_json()}")
                return False
            print_pass(f"Characters endpoint OK (status: {response1.status_code})")
            
            cache_status_1 = response1.headers.get('X-Cache', 'unknown')
            print_pass(f"First request cache status: {cache_status_1}")
            
            if cache_status_1 not in ['miss', 'bypass']:
                print_warn(f"Expected 'miss' or 'bypass' for first request, got '{cache_status_1}'")
            
            # Test 5.3: Characters endpoint (second request - should be cache hit if not bypass)
            logger.info("Testing /characters endpoint (second request)...")
            time.sleep(0.1)  # Small delay
            response2 = client.get('/characters')
            
            if response2.status_code != 200:
                print_fail(f"Second request failed: {response2.status_code}")
                return False
            
            cache_status_2 = response2.headers.get('X-Cache', 'unknown')
            print_pass(f"Second request cache status: {cache_status_2}")
            
            # Verify both responses have same content (if cached correctly)
            data1 = response1.get_json()
            data2 = response2.get_json()
            
            if data1 != data2:
                print_fail("Response data differs between requests (cache issue)")
                return False
            print_pass("Response data consistent between requests")
            
            # Test 5.4: Cache headers present
            required_headers = ['X-Cache', 'X-Cache-Key', 'Cache-Control', 'Vary']
            for header in required_headers:
                if header not in response2.headers:
                    print_fail(f"Missing required header: {header}")
                    return False
            print_pass(f"All required headers present: {required_headers}")
        
        print_pass("All middleware functionality tests passed")
        return True
        
    except Exception as e:
        print_fail(f"Exception during middleware test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  PRE-DOCKER BUILD VALIDATION TEST SUITE                    ║")
    print("║  Rick and Morty Character API                              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    tests = [
        ("Cache Backend Storage", test_cache_backend_storage),
        ("Database Connection", test_database_connection),
        ("Flask App Init", test_flask_app_initialization),
        ("Endpoint Routing", test_endpoint_routing),
        ("Middleware Functionality", test_middleware_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Test crashed: {type(e).__name__}: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  [{status}] {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED - Safe to proceed with Docker build{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED - Fix issues before Docker build{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
