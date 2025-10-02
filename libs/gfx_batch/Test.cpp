// Copyright (c) Facebook, Inc. and its affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.



#include <Magnum/Math/Vector2.h>

#include "RendererStandalone.h"

// temp
#include <Corrade/Containers/Triple.h>
#include <Corrade/PluginManager/PluginMetadata.h>
#include <Corrade/TestSuite/Compare/File.h>
#include <Corrade/TestSuite/Tester.h>
#include <Corrade/Utility/ConfigurationGroup.h>
#include <Corrade/Utility/Path.h>
#include <Magnum/DebugTools/CompareImage.h>
#include <Magnum/GL/OpenGLTester.h> /* just for MAGNUM_VERIFY_NO_GL_ERROR() */
#include <Magnum/GL/BufferImage.h>
#include <Magnum/GL/Framebuffer.h>
#include <Magnum/GL/Renderbuffer.h>
#include <Magnum/GL/RenderbufferFormat.h>
#include <Magnum/Image.h>
#include <Magnum/ImageView.h>
#include <Magnum/Math/Color.h>
#include <Magnum/Math/Range.h>
#include <Magnum/MeshTools/Combine.h>
#include <Magnum/MeshTools/Concatenate.h>
#include <Magnum/MeshTools/GenerateIndices.h>
#include <Magnum/MeshTools/Transform.h>
#include <Magnum/Primitives/Circle.h>
#include <Magnum/Primitives/Plane.h>
#include <Magnum/Primitives/UVSphere.h>
#include <Magnum/SceneTools/Hierarchy.h>
#include <Magnum/Trade/AbstractImageConverter.h>
#include <Magnum/Trade/AbstractSceneConverter.h>
#include <Magnum/Trade/MaterialData.h>
#include <Magnum/Trade/MeshData.h>
#include <Magnum/Trade/SceneData.h>
#include <Magnum/Trade/TextureData.h>

#include <cassert>

namespace Mn = Magnum;
using namespace Mn::Math::Literals;

namespace gfx_batch {

void testRendererStandalone() {

  // clang-format off
  gfx_batch::RendererStandalone renderer{
      gfx_batch::RendererConfiguration{}
          .setTileSizeCount({48, 32}, {2, 3}),
      gfx_batch::RendererStandaloneConfiguration{}
          .setFlags(gfx_batch::RendererStandaloneFlags{})
  };

  renderer.draw();
  Mn::Image2D color = renderer.colorImage();
  Mn::Image2D depth = renderer.depthImage();
  //MAGNUM_VERIFY_NO_GL_ERROR();
  assert(Magnum::GL::Renderer::error() == Magnum::GL::Renderer::Error::NoError);

  /* Verify the color actually matches expectation so we don't need to manually
     color pick the image every time it changes */
  assert(color.size() == Mn::Vector2i{96});
  assert(color.format() == Mn::PixelFormat::RGBA8Unorm);
  assert(color.pixels<Mn::Color4ub>()[48][48] == 0x1f1f1fff_rgba);

  /* Verify the depth readout works as well. Also should be a single value. */
  assert(depth.size() == Mn::Vector2i{96});
  assert(depth.format() == Mn::PixelFormat::Depth32F);
  assert(depth.pixels<Mn::Float>()[48][48] == 1.0f);


}

}
