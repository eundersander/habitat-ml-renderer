#!/bin/bash

# Build script for habitat monorepo C++ components
# This builds all C++ libraries and Python extensions to the install/ directory
#
# Prerequisites:
# - Activate your mamba environment with cmake, pybind11, and pytorch installed
# - Example: mamba activate your_env

set -e  # Exit on any error

echo "Building C++ components..."

# Configure and build
cmake -B cpp/build -S cpp
cmake --build cpp/build --parallel --target install

echo "C++ build complete! Built libraries are in install/"
echo "You can now run: pip install -e python/habitat_ml_renderer/"