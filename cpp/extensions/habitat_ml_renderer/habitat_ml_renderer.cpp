// Copyright (c) Facebook, Inc. and its affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

// cmake todo: require these includes to be qualified by path, e.g. "gfx_batch/RendererStandalone.h"
#include "RendererStandalone.h"
#include "Test.h"

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include <Magnum/Math/Vector2.h>
#include <Magnum/Math/Matrix4.h>
#include <Corrade/Containers/StringStl.h>

namespace py = pybind11;
using py::literals::operator""_a;
using namespace gfx_batch;
namespace Mn = Magnum;

namespace {

// only enable VALIDATE on debug builds
#ifdef NDEBUG
#define VALIDATE(condition)
#else
#define VALIDATE(condition) \
    do { \
        if (!(condition)) { \
            throw py::value_error("Validation failed in file " + std::string(__FILE__) + ":" + std::to_string(__LINE__)); \
        } \
    } while (false)
#endif

template <typename... Ts>
bool compare_shape(py::array_t<float> myarr, std::tuple<Ts...> expected_shape_tuple) {
    std::vector<py::ssize_t> expected_shape;
    std::apply([&](auto&&... args) { (expected_shape.push_back(args), ...); }, expected_shape_tuple);
    return std::vector<py::ssize_t>(myarr.shape(), myarr.shape() + myarr.ndim()) == expected_shape;
}

Magnum::Matrix4 toMagnumMatrix4(py::array_t<float>& pyarr, int sceneId) {

  // VALIDATE(projection.ndim() == 3);
  // VALIDATE(pyarr.shape(0) > sceneId);
  // VALIDATE(projection.shape(1) == 4);
  // VALIDATE(projection.shape(2) == 4);

  const auto& sc = sceneId;
  const auto& p = pyarr;

  Magnum::Matrix4 matrix{
     {p.at(sc, 0, 0),
      p.at(sc, 0, 1),
      p.at(sc, 0, 2),
      p.at(sc, 0, 3)},
     {p.at(sc, 1, 0),
      p.at(sc, 1, 1),
      p.at(sc, 1, 2),
      p.at(sc, 1, 3)},
     {p.at(sc, 2, 0),
      p.at(sc, 2, 1),
      p.at(sc, 2, 2),
      p.at(sc, 2, 3)},
     {p.at(sc, 3, 0),
      p.at(sc, 3, 1),
      p.at(sc, 3, 2),
      p.at(sc, 3, 3)},
  };
  return matrix;
}

}

PYBIND11_MODULE(habitat_ml_renderer, m) {
   m.attr("hello_world") = true;
   m.def("testRendererStandalone", &testRendererStandalone, "A function that calls the C++ test function");
      
  py::class_<RendererStandalone>(m, "RendererStandalone")


      .def(py::init([](py::kwargs kwargs) {
        // Check that the required arguments are present
        if(kwargs.contains("image_width") && kwargs.contains("image_height") && kwargs.contains("num_envs")) {
          // Extract the arguments
          int image_width = kwargs["image_width"].cast<int>();
          int image_height = kwargs["image_height"].cast<int>();
          int num_envs = kwargs["num_envs"].cast<int>();
  
          auto numColorChannels = 3; // todo: hook up to RendererStandalone's pixel format
          auto tileSize = Magnum::Vector2i(image_width, image_height);
          // note that tileCount.x must be 1 to ensure a linear buffer memory layout that can be reinterpreted as (numColorChannels x imageWidth x imageHeight x numEnvs)
          auto tileCount = Magnum::Vector2i(1, num_envs);
          return std::make_unique<RendererStandalone>(
              RendererConfiguration{}
                  .setTileSizeCount(tileSize, tileCount),
              RendererStandaloneConfiguration{}
                  .setFlags(RendererStandaloneFlags{})
          );
        } else {
          throw std::runtime_error("Missing required keyword arguments: image_width, image_height, num_envs");
        }
      }))

      .def("draw", &RendererStandalone::draw)

      .def("add_file", [](RendererStandalone& self, const std::string& filename, const std::string& name, bool whole, bool generate_mipmap) -> bool {
          RendererFileFlags flags;
          if (whole) { flags |= RendererFileFlag::Whole; }
          if (generate_mipmap) { flags |= RendererFileFlag::GenerateMipmap; }
          auto result = self.addFile(filename, flags, name);
          if (!result) {
              throw py::value_error(std::string("Failed to add file '") + filename + "'");
          }
          return result;
      }, py::arg("filename"), py::arg("name") = "", py::arg("whole") = false, py::arg("generate_mipmap") = false)

      .def("add_node_hierarchy", [](RendererStandalone& self, int scene_id, const std::string& name) -> size_t {
          return self.addNodeHierarchy(scene_id, name, Magnum::Matrix4{});
      })

      .def("add_node_hierarchy", [](RendererStandalone& self, int scene_id, const std::string& name, const std::vector<float>& bake_transformation) -> size_t {
          if (bake_transformation.size() != 16) {
            throw py::value_error("Expected len(bake_transformation) == 16 representing a 4x4 matrix");
          }
          const auto& m = bake_transformation;
          Magnum::Matrix4 matrix{
            {m[0], m[1], m[2], m[3]},
            {m[4], m[5], m[6], m[7]},
            {m[8], m[9], m[10], m[11]},
            {m[12], m[13], m[14], m[15]},
          };
          return self.addNodeHierarchy(scene_id, name, matrix);
      })
      
      .def("add_node_hierarchy", [](RendererStandalone& self, int scene_id, const std::string& name) -> size_t {
          return self.addNodeHierarchy(scene_id, name, Magnum::Matrix4{});
      })      
      .def("update_camera", [](RendererStandalone& self, py::array_t<float> projection, py::array_t<float> view) {
        int numScenes = self.sceneCount();
        VALIDATE(compare_shape(projection, std::make_tuple(numScenes, 4, 4)));
        VALIDATE(compare_shape(view, std::make_tuple(numScenes, 4, 4)));

        // perf todo: faster way to send these matrices to the renderer
        for (int sceneId = 0; sceneId < numScenes; sceneId++) {

          auto tmpViewProj = self.camera(sceneId);
          auto tmp = toMagnumMatrix4(projection, sceneId);
          auto tmp2 = Mn::Matrix4::perspectiveProjection(Mn::Rad(Mn::Deg(60.0)), 256.f / 192.f, 0.01, 10.0);
          auto viewMat = toMagnumMatrix4(view, sceneId);
          auto viewMat2 = Mn::Matrix4::lookAt(Mn::Vector3{0, 1, -4}, Mn::Vector3{0, 0.0, 0}, Mn::Vector3{0, 1.0, 0});
          self.updateCamera(sceneId, tmp, viewMat);
        }
      })

      .def(
          "rgba",
          [](gfx_batch::RendererStandalone& self) {
            return py::capsule(self.colorCudaBufferDevicePointer());
          },
          R"(todo)")
      .def(
          "depth",
          [](gfx_batch::RendererStandalone& self) {
            return py::capsule(self.depthCudaBufferDevicePointer());
          },
          R"(todo)") 
      ;       
}
