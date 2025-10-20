#!/bin/bash

# Function to check the exit status of a command and exit if it failed
check_command() {
  if [ $? -ne 0 ]; then
    echo "Error: $1 failed" >&2
    exit 1
  fi
}

# portable "number of CPUs"
if command -v nproc >/dev/null 2>&1; then
    JOBS=$(nproc)
else
    JOBS=$(sysctl -n hw.ncpu)
fi

# Helper function to clean and create the build directory
clean_and_create_build_dir() {
  # If --clean was provided, remove the build directory
  if [ $CLEAN -eq 1 ] && [ -d "${BUILD_DIR}" ]; then
    rm -rf ${BUILD_DIR}
  fi
  # Create the build directory if it doesn't exist
  mkdir -p ${BUILD_DIR} && cd ${BUILD_DIR}
}

# Set the default build type and directory
BUILD_TYPE="Release"
BUILD_DIR="build"
CLEAN=0

# Process the command-line arguments
for arg in "$@"
do
  if [ "$arg" == "--debug" ]; then
    # If --debug is provided, set the build type to Debug and the directory to build_debug
    BUILD_TYPE="Debug"
    BUILD_DIR="build_debug"
  elif [ "$arg" == "--clean" ]; then
    # If --clean is provided, set the CLEAN variable
    CLEAN=1
  fi
done

# Clone the corrade repository if it doesn't exist
if [ ! -d "mochi" ]; then
  git clone https://github.com/facebookresearch/mochi
  check_command "Cloning mochi repository"
fi
cd mochi
clean_and_create_build_dir

# Run CMake and make
cmake -DMOCHI_USE_PYBIND=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=1 ..
cmake --build . -- -j$(nproc)
check_command "Build and install mochi"
cd ../../

EXT_SRC="mochi/build/pybind/mochi.so"
if [ ! -f "$EXT_SRC" ]; then
  echo "Error: Python extension not found at $EXT_SRC" >&2
  exit 1
fi

STAGE_DIR="mochi/python/mochi"
mkdir -p "$STAGE_DIR"

# Keep the original filename (mochi.so)
cp "$EXT_SRC" "$STAGE_DIR/mochi.so"

# Make sure Python imports it
echo "from .mochi import *" > "$STAGE_DIR/__init__.py"

# Write minimal pyproject.toml so pip includes the .so file
cat > mochi/python/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "mochi"
version = "0.1"

[tool.setuptools.package-data]
mochi = ["*.so"]
EOF

# Post-build message
cat <<EOF

Mochi build complete.
To install it into your current environment, run:
  pip install ./mochi/python

If you also want to install mochi_gym:
  pip install -e ./mochi/mochi_gym
EOF




