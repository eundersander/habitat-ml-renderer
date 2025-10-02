# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

corrade_add_test(
  GfxBatchHbaoTest
  GfxBatchHbaoTest.cpp
  LIBRARIES
  gfx_batch
  Magnum::DebugTools
  Magnum::OpenGLTester
  Magnum::MeshTools
  # Magnum::AnyImageConverter
  Magnum::AnyImageImporter
  Magnum::AnySceneImporter
#   MagnumPlugins::OpenExrImageConverter
#   MagnumPlugins::OpenExrImporter
#   MagnumPlugins::StanfordImporter
#   MagnumPlugins::StbImageImporter
#   MagnumPlugins::StbImageConverter
)
target_include_directories(GfxBatchHbaoTest PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

corrade_add_test(
  GfxBatchRendererTest
  GfxBatchRendererTest.cpp
  LIBRARIES
  gfx_batch
  Magnum::DebugTools
  # Magnum::AnyImageConverter
  Magnum::AnySceneImporter
#   MagnumPlugins::GltfImporter
#   MagnumPlugins::KtxImporter
#   MagnumPlugins::StbImageImporter
#   MagnumPlugins::StbImageConverter
)
target_include_directories(GfxBatchRendererTest PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
if(BUILD_WITH_CUDA)
  target_include_directories(
    GfxBatchRendererTest PRIVATE ${CMAKE_CUDA_TOOLKIT_INCLUDE_DIRECTORIES}
  )
endif()
if(MagnumPlugins_GltfSceneConverter_FOUND)
  target_link_libraries(GfxBatchRendererTest PRIVATE MagnumPlugins::GltfSceneConverter)
endif()
if(MagnumPlugins_KtxImageConverter_FOUND)
  target_link_libraries(GfxBatchRendererTest PRIVATE MagnumPlugins::KtxImageConverter)
endif()
