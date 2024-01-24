# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# todo: figure out what to put here
cmake_minimum_required(VERSION 3.12)

# some cmake policy stuff copied from magnum-examples
# Don't restrict INTERPROCEDURAL_OPTIMIZATION only for icc on Linux
if(POLICY CMP0069)
    cmake_policy(SET CMP0069 NEW)
endif()
# If CMAKE_AUTOMOC is set, all uses of corrade_add_resource() would otherwise
# complain on 3.10 that AUTOMOC is not processing GENERATED files
if(POLICY CMP0071)
    cmake_policy(SET CMP0071 NEW)
endif()
# Allow <PackageName>_ROOT to be used on 3.12+ to point to per-package install
# locations that find_package(PackageName) subsequently picks up
if(POLICY CMP0074)
    cmake_policy(SET CMP0074 NEW)
endif()
# Allow also <PACKAGENAME>_ROOT (i.e., uppercase), on 3.27+
if(POLICY CMP0144)
    cmake_policy(SET CMP0144 NEW)
endif()
# Superprojects can use just set(MAGNUM_WITH_BLAH ON) without FORCE CACHE on
# 3.13+
if(POLICY CMP0077)
    cmake_policy(SET CMP0077 NEW)
endif()

# something about a list command used by Magnum
if(POLICY CMP0057)
    cmake_policy(SET CMP0057 NEW)
endif()

# something else about a list command used by Magnum
if(POLICY CMP0007)
    cmake_policy(SET CMP0007 NEW)
endif()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# todo: figure out what to use for project and what to put for languages
project(my_project LANGUAGES C CXX)

set(CMAKE_PREFIX_PATH "/home/eundersander/mambaforge/envs/habitat_ml_renderer1/lib/python3.11/site-packages")

# this is not working; not sure why
# set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/external/install_root")

# todo: when this is off, figure out why we hit runtime undefined symbol: cudaGraphicsMapResources
set(BUILD_WITH_CUDA ON)


enable_language(CUDA)

include_directories("/usr/local/cuda-12.3/targets/x86_64-linux/include")

set(PYBIND11_PYTHON_VERSION 3.7 CACHE STRING "")
# you should have invoked with cmake -DCMAKE_PREFIX_PATH=/path/to/pybind11 ..
find_package(pybind11 REQUIRED)

find_package(
  Magnum
  REQUIRED
  GL
  SceneTools
  Shaders
  Trade
)
find_package(Corrade REQUIRED Utility)

add_subdirectory(gfx_batch)
add_subdirectory(bindings)