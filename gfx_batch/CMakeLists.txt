# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
  Test.cpp
  Test.h
)

set_directory_properties(PROPERTIES CORRADE_USE_PEDANTIC_FLAGS ON)
corrade_add_resource(GfxBatchShaderResources ../shaders/gfx_batch/Shaders.conf)
list(APPEND gfx_batch_SOURCES ${GfxBatchShaderResources})

add_library(
  gfx_batch STATIC
  ${gfx_batch_SOURCES}
)

# make this library's headers available to users
target_include_directories(gfx_batch PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

if(BUILD_WITH_CUDA)
  find_package(CUDA REQUIRED)
  target_include_directories(
    gfx_batch PUBLIC ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}
                     ${CMAKE_CURRENT_LIST_DIR}/cuda_helpers
  )
  target_link_libraries(gfx_batch PUBLIC ${CUDA_LIBRARIES})
  message("CUDA_LIBRARIES: ${CUDA_LIBRARIES}")  
else()
  message("BUILD_WITH_CUDA is off")
endif()


if(MAGNUM_TARGET_EGL)
  set(WINDOWLESS_APPLICATION_PACKAGE "WindowlessEglApplication")
elseif(CORRADE_TARGET_UNIX)
  set(WINDOWLESS_APPLICATION_PACKAGE "WindowlessGlxApplication")
else()
  message(FATAL_ERROR "Unsupported platform")
endif()

find_package(Magnum REQUIRED 
  ${WINDOWLESS_APPLICATION_PACKAGE} 
  MeshTools
  OpenGLTester
  DebugTools)

target_link_libraries(
  gfx_batch
  # Important: this library *deliberately* doesn't depend on any other Habitat
  # libraries, and it should be kept as such. Only Magnum libraries are an
  # allowed dependency. See the original PR for discussion:
  # https://github.com/facebookresearch/habitat-sim/pull/1798#discussion_r911398937
  PUBLIC Magnum::GL
         Magnum::Magnum
         Magnum::SceneTools
         Magnum::MeshTools
         Magnum::Shaders
         Magnum::Trade
         Magnum::WindowlessApplication
         Magnum::OpenGLTester
         Magnum::DebugTools
  # Not linking any plugins here, as the renderer itself doesn't directly rely
  # on any of them. That also makes the plugins implicitly registered in
  # *every* target that links to gfx_batch, which is far from ideal. Only the
  # leaf executable links to them, and only to those that are actually used
  # in that scenario -- i.e., a test only needs a tiny subset of plugins for
  # data it uses, not everything to handle general file formats.
)
