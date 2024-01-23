# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# todo: figure out what to put here
cmake_minimum_required(VERSION 3.12)

# todo: figure out what to use for project and what to put for languages
project(my_project LANGUAGES C CXX)

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

find_package(
  Magnum
  REQUIRED
  GL
  SceneTools
  Shaders
  Trade
)
find_package(Corrade REQUIRED Utility)

set(
  gfx_batch_SOURCES
  DepthUnprojection.cpp
  DepthUnprojection.h
  Renderer.cpp
  Renderer.h
  RendererStandalone.cpp
  RendererStandalone.h
  Hbao.cpp
  Hbao.h
)

set_directory_properties(PROPERTIES CORRADE_USE_PEDANTIC_FLAGS ON)
corrade_add_resource(GfxBatchShaderResources ../shaders/gfx_batch/Shaders.conf)
list(APPEND gfx_batch_SOURCES ${GfxBatchShaderResources})

add_library(
  gfx_batch STATIC
  ${gfx_batch_SOURCES}
)
# For esp/core/configure.h
# TODO move configure.h directly to esp/
target_include_directories(gfx_batch PUBLIC ${PROJECT_BINARY_DIR})
if(BUILD_WITH_CUDA)
  target_include_directories(
    gfx_batch PUBLIC ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}
                     ${CMAKE_CURRENT_LIST_DIR}/cuda_helpers
  )

  target_link_libraries(gfx_batch PUBLIC ${CUDART_LIBRARY})
endif()

# Find appropriate windowless library for the standalone renderer
if(MAGNUM_TARGET_EGL)
  # Includes also Emscripten
  find_package(Magnum REQUIRED WindowlessEglApplication)
elseif(CORRADE_TARGET_APPLE)
  find_package(Magnum REQUIRED WindowlessCglApplication)
elseif(CORRADE_TARGET_UNIX)
  # Mainly for builds with external Magnum that might not have TARGET_EGL
  # enabled
  find_package(Magnum REQUIRED WindowlessGlxApplication)
elseif(CORRADE_TARGET_WINDOWS)
  find_package(Magnum REQUIRED WindowlessWglApplication)
else()
  message(FATAL_ERROR "Unsupported platform")
endif()

target_link_libraries(
  gfx_batch
  # Important: this library *deliberately* doesn't depend on any other Habitat
  # libraries, and it should be kept as such. Only Magnum libraries are an
  # allowed dependency. See the original PR for discussion:
  # https://github.com/facebookresearch/habitat-sim/pull/1798#discussion_r911398937
  PUBLIC Magnum::GL
         Magnum::Magnum
         Magnum::SceneTools
         Magnum::Shaders
         Magnum::Trade
         Magnum::WindowlessApplication
  # Not linking any plugins here, as the renderer itself doesn't directly rely
  # on any of them. That also makes the plugins implicitly registered in
  # *every* target that links to gfx_batch, which is far from ideal. Only the
  # leaf executable links to them, and only to those that are actually used
  # in that scenario -- i.e., a test only needs a tiny subset of plugins for
  # data it uses, not everything to handle general file formats.
)
