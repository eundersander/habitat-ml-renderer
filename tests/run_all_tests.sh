#!/bin/bash

# Run all tests for the habitat monorepo
# This includes both C++ and Python integration tests

set -e

echo "Running Habitat monorepo tests..."

# Check if we're in the right directory
if [[ ! -f "tools/build_cpp.sh" ]]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

echo "1. Testing project structure..."
if [[ -d "cpp" && -d "python" && -d "tests" && -d "tools" ]]; then
    echo "✅ Project structure looks good"
else
    echo "❌ Project structure is incomplete"
    exit 1
fi

echo ""
echo "2. Running Python integration tests..."
if command -v pytest >/dev/null 2>&1; then
    pytest tests/ -v
    echo "✅ Python tests completed"
else
    echo "⚠️  pytest not available, skipping Python tests"
fi

echo ""
echo "3. Running C++ integration tests..."
if [[ -f "install/bin/test_integration" ]]; then
    ./install/bin/test_integration
    echo "✅ C++ tests completed"
else
    echo "⚠️  C++ tests not built yet, run tools/build_cpp.sh first"
fi

echo ""
echo "4. Testing package installation (dry run)..."
if [[ -f "python/habitat_ml_renderer/setup.py" ]]; then
    echo "✅ Python packages ready for installation"
else
    echo "❌ Python package setup files missing"
fi

echo ""
echo "Test summary completed!"
echo ""
echo "To fully test the system:"
echo "1. Run: ./tools/build_magnum.sh    (build graphics dependencies)"
echo "2. Run: ./tools/build_cpp.sh       (build C++ components)"
echo "3. Run: pip install -e python/habitat_ml_renderer/"
echo "4. Run: ./tests/run_all_tests.sh   (run this script again)"