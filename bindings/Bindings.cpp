// Copyright (c) Facebook, Inc. and its affiliates.
// This source code is licensed under the MIT license found in the
// LICENSE file in the root directory of this source tree.

// cmake todo: require these includes to be qualified by path, e.g. "gfx_batch/RendererStandalone.h"
#include "RendererStandalone.h"
#include "Test.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;
using py::literals::operator""_a;

PYBIND11_MODULE(habitat_ml_renderer_python, m) {
   m.attr("hello_world") = true;
   m.def("testRendererStandalone", &gfx_batch::testRendererStandalone, "A function that calls the C++ test function");
}
