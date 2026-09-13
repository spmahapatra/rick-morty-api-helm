#!/usr/bin/env python3
"""
Quick Cache Validation Script
Runs essential cache validation tests and reports results
"""

import sys
import time
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run cache validation suite"""
    
    print("\n" + "="*60)
    print("🚀 CACHE FEATURE VALIDATION SUITE")
    print("="*60)
    
    results = {}
    
    # Test 1: Unit tests
    results["Unit Tests"] = run_command(
        "pytest tests/test_cache.py -v --tb=short",
        "Test 1: Running Cache Unit Tests"
    )
    
    # Test 2: Cache backend initialization
    print(f"\n{'='*60}")
    print("Test 2: Testing Cache Backend Initialization")
    print(f"{'='*60}")
    try:
        from src.cache import InMemoryBackend, RedisBackend
        
        # Test InMemoryBackend
        in_memory = InMemoryBackend()
        print("✅ InMemoryBackend initialized successfully")
        assert in_memory.ping() is True
        print("✅ InMemoryBackend ping successful")
        
        # Test basic operations
        in_memory.set("test_key", {"data": "value"}, ttl_seconds=300)
        result = in_memory.get("test_key")
        assert result == {"data": "value"}
        print("✅ Set/Get operations successful")
        
        # Test stats
        stats = in_memory.get_stats()
        print(f"✅ Cache stats: {stats}")
        
        results["Backend Init"] = True
    except Exception as e:
        print(f"❌ Backend initialization failed: {e}")
        results["Backend Init"] = False
    
    # Test 3: TTL expiration
    print(f"\n{'='*60}")
    print("Test 3: Testing TTL Expiration")
    print(f"{'='*60}")
    try:
        from src.cache import InMemoryBackend
        
        cache = InMemoryBackend()
        cache.set("expire_test", "value", ttl_seconds=2)
        
        # Should exist immediately
        assert cache.exists("expire_test") is True
        print("✅ Entry exists immediately after set")
        
        # Wait for expiration
        print("⏳ Waiting for TTL expiration (2 seconds)...")
        time.sleep(2.1)
        
        # Should be expired
        assert cache.exists("expire_test") is False
        print("✅ Entry expired after TTL")
        
        results["TTL Expiration"] = True
    except Exception as e:
        print(f"❌ TTL test failed: {e}")
        results["TTL Expiration"] = False
    
    # Test 4: Cache statistics
    print(f"\n{'='*60}")
    print("Test 4: Testing Cache Statistics")
    print(f"{'='*60}")
    try:
        from src.cache import InMemoryBackend
        
        cache = InMemoryBackend()
        
        # Simulate operations
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("missing")  # miss
        
        stats = cache.get_stats()
        
        print(f"Hits: {stats['hits']}")
        print(f"Misses: {stats['misses']}")
        print(f"Hit Ratio: {stats['hit_ratio']}%")
        print(f"Backend: {stats['backend']}")
        print(f"Connected: {stats['connected']}")
        
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_ratio'] > 0
        print("✅ Cache statistics working correctly")
        
        results["Statistics"] = True
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        results["Statistics"] = False
    
    # Test 5: Cache decorator
    print(f"\n{'='*60}")
    print("Test 5: Testing Cache Decorator")
    print(f"{'='*60}")
    try:
        from src.cache import InMemoryBackend, cached
        
        cache = InMemoryBackend()
        call_count = 0
        
        @cached(ttl_seconds=300)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": "computed"}
        
        # First call
        result1 = expensive_function(cache)
        assert result1 == {"result": "computed"}
        assert call_count == 1
        print("✅ First function call executed")
        
        # Second call (should use cache)
        result2 = expensive_function(cache)
        assert result2 == {"result": "computed"}
        assert call_count == 1  # Still 1, cache hit!
        print("✅ Second function call used cache (not executed)")
        
        results["Decorator"] = True
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        results["Decorator"] = False
    
    # Test 6: Complex data serialization
    print(f"\n{'='*60}")
    print("Test 6: Testing Complex Data Serialization")
    print(f"{'='*60}")
    try:
        from src.cache import InMemoryBackend
        
        cache = InMemoryBackend()
        
        complex_data = {
            "characters": [
                {"id": 1, "name": "Rick", "status": "alive"},
                {"id": 2, "name": "Morty", "status": "alive"}
            ],
            "metadata": {
                "total": 2,
                "page": 1,
                "per_page": 10
            }
        }
        
        cache.set("complex", complex_data)
        retrieved = cache.get("complex")
        
        assert retrieved == complex_data
        print("✅ Complex data structures serialize/deserialize correctly")
        
        results["Complex Data"] = True
    except Exception as e:
        print(f"❌ Complex data test failed: {e}")
        results["Complex Data"] = False
    
    # Test 7: Graceful degradation (Redis unavailable)
    print(f"\n{'='*60}")
    print("Test 7: Testing Graceful Degradation")
    print(f"{'='*60}")
    try:
        from src.cache import RedisBackend
        
        # Try to connect to invalid Redis
        backend = RedisBackend("redis://invalid:1234/0")
        
        # Should handle gracefully
        assert backend.get("key") is None
        assert backend.set("key", "value") is False
        assert backend.ping() is False
        print("✅ Gracefully handles Redis connection failures")
        
        results["Graceful Degradation"] = True
    except Exception as e:
        print(f"❌ Graceful degradation test failed: {e}")
        results["Graceful Degradation"] = False
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All cache validation tests passed!")
        print("\nNext steps:")
        print("  1. Run 'pytest tests/ -v' for comprehensive test suite")
        print("  2. Run 'python app.py' to start the API")
        print("  3. Test with 'curl http://localhost:5000/cache/stats' (if endpoint exists)")
        print("  4. Review CACHE_VALIDATION_GUIDE.md for detailed validation procedures")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
