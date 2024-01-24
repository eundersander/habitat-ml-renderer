#!/bin/bash
# Function to check the exit status of a command and exit if it failed
check_command() {
  if [ $? -ne 0 ]; then
    echo "Error: $1 failed" >&2
    exit 1
  fi
}
# Create the external directory if it doesn't exist
mkdir -p external && cd external
# Create the install_root directory if it doesn't exist
mkdir -p install_root
# Clone the corrade repository if it doesn't exist
if [ ! -d "corrade" ]; then
  git clone https://github.com/mosra/corrade.git
  check_command "Cloning corrade repository"
fi
cd corrade
# Create the build directory if it doesn't exist
mkdir -p build && cd build
# Run CMake and make
cmake -DCMAKE_INSTALL_PREFIX=../../install_root ..
check_command "Running CMake for corrade"
make
check_command "Building corrade"
make install
cd ../../
# Clone the magnum repository if it doesn't exist
if [ ! -d "magnum" ]; then
  git clone https://github.com/mosra/magnum.git
  check_command "Cloning magnum repository"
fi
cd magnum
# Create the build directory if it doesn't exist
mkdir -p build && cd build
# Run CMake and make
cmake -DCMAKE_INSTALL_PREFIX=../../install_root -DMAGNUM_WITH_WINDOWLESSGLXAPPLICATION=ON -DMAGNUM_WITH_OPENGLTESTER=ON ..
check_command "Running CMake for magnum"
make
check_command "Building magnum"
make install
cd ../../
# Clone the magnum-bindings repository if it doesn't exist
if [ ! -d "magnum-bindings" ]; then
  git clone https://github.com/mosra/magnum-bindings.git
  check_command "Cloning magnum-bindings repository"
fi
cd magnum-bindings
# Create the build directory if it doesn't exist
mkdir -p build && cd build
# Run CMake and make
cmake -DCMAKE_INSTALL_PREFIX=../../install_root ..
check_command "Running CMake for magnum-bindings"
make
check_command "Building magnum-bindings"
make install
