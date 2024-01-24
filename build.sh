#!/bin/bash
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
cmake -DCMAKE_BUILD_TYPE=${BUILD_TYPE} -DCMAKE_INSTALL_PREFIX=../external/install_root ..
# Run make to build the project
make && cp ./bindings/*.so ../