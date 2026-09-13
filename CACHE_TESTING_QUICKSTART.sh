#!/bin/bash

# Cache Feature Testing - Quick Start Script
# Run this to validate the cache feature end-to-end

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        CACHE FEATURE VALIDATION - QUICK START              ║"
echo "║     This script validates all cache functionality           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate || {
    echo "❌ Failed to activate venv. Make sure you're in the project root."
    exit 1
}
echo "✅ Virtual environment activated"
echo ""

# Run validation script
echo "🧪 Running validation tests..."
python3 validate_cache.py
VALIDATION_RESULT=$?
echo ""

# Run pytest if validation passed
if [ $VALIDATION_RESULT -eq 0 ]; then
    echo "📊 Running pytest suite..."
    pytest tests/test_cache.py -v --tb=short
    PYTEST_RESULT=$?
    echo ""
    
    if [ $PYTEST_RESULT -eq 0 ]; then
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║            ✅ ALL CACHE TESTS PASSED                       ║"
        echo "╠════════════════════════════════════════════════════════════╣"
        echo "║                                                            ║"
        echo "║  The cache feature is fully validated and working!         ║"
        echo "║                                                            ║"
        echo "║  📚 Documentation:                                         ║"
        echo "║     - CACHE_VALIDATION_GUIDE.md      (comprehensive)      ║"
        echo "║     - CACHE_VALIDATION_SUMMARY.md    (quick reference)    ║"
        echo "║     - validate_cache.py               (automated testing)  ║"
        echo "║                                                            ║"
        echo "║  🚀 Next Steps:                                            ║"
        echo "║     1. python3 app.py                 (start API)          ║"
        echo "║     2. curl http://localhost:5000/characters              ║"
        echo "║     3. Monitor cache stats in app                         ║"
        echo "║                                                            ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        exit 0
    else
        echo "⚠️  Some pytest tests failed. Review output above."
        exit 1
    fi
else
    echo "⚠️  Some validation tests failed. Review output above."
    exit 1
fi
