#!/bin/bash

# Get the site-packages directory
PYTHON_SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
# Check if the pybind11 directory exists
if [ ! -d "${PYTHON_SITE_PACKAGES}/pybind11" ]; then
  echo "Error: pybind11 directory not found at ${PYTHON_SITE_PACKAGES}" >&2
  exit 1
fi

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
# If --clean was provided, remove the build directory
if [ $CLEAN -eq 1 ] && [ -d "${BUILD_DIR}" ]; then
  rm -rf ${BUILD_DIR}
fi
# Create the build directory if it doesn't exist
if [ ! -d "${BUILD_DIR}" ]; then
  mkdir ${BUILD_DIR}
fi
# Navigate into the build directory
cd ${BUILD_DIR}
# Run CMake with the specified build type
# Maybe MAGNUM_TARGET_EGL=ON is needed here? See also build_magnum.sh
cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} -DCMAKE_INSTALL_PREFIX=../magnum_root/install_root -DCMAKE_PREFIX_PATH=${PYTHON_SITE_PACKAGES} -DMAGNUM_TARGET_EGL=ON ..
# Run make to build the project
make && cp ./habitat_ml_renderer/*.so ../