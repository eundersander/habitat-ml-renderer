

# Habitat-ml-renderer

A python extension module for loading 3D scenes, batch-rendering them via OpenGL, and exposing the resulting batch of images as a PyTorch CUDA tensor (RGB and/or depth).

This package is based on [Habitat-sim](https://github.com/facebookresearch/habitat-sim) but aims to have minimal dependencies (mostly Magnum, PyTorch, and CUDA Toolkit so far).


# Todo
* Flesh out our python test ([test.py](./test.py))
    * Fix the unintuitive python interfaces for creating image tensors and updating them after drawing.
        * Currently, the confusingly-named `rgba` is used for both creating and updating.
        * The C++ function `Renderer::colorCudaBufferDevicePointer` is also misleading because it suggests you only need to call it once at startup; you actually have to call this after every draw.
        * We need to update both the RGB and depth interfaces.
    * Update instances between draws using `Renderer::transformations` (add bindings as necessary); render multiple images.
    * Experiment with lights (add bindings as necessary).
* Repo cleanup
    * Currently the habitat_ml_renderer extension `.so` is copied to the project root but not actually installed into the python environment.
    * The project root folder is too cluttered.
* 3D model preprocess pipeline
    * (Currently we can load GLTF files with `add_file`.)
    * Provide a preprocess pipeline/documentation for converting other 3D model formats to GLTF.
* URDF and per-instance color-override support
    * Add color-override support and URDF-parsing. Many users are using URDF files which specify a set of 3D models along with per-instance color overrides.
    * This could be part of the preprocess pipeline and/or part of the runtime API.
* Composite GLTF pipeline
    * In terms of rendering speed, the renderer will benefit from the use of "composite" GLTF/GLB files. We should document how to build and use these.

# Directory structure

* `habitat_ml_renderer:` the Python extension module. It's primarily C++ pybind11 code wrapping renderer functionality provided by `gfx_batch`.
* `gfx_batch:` a pure C++ library that implements the renderer (on top of Magnum). It's essentially a copy-paste of the [`esp/gfx_batch`](https://github.com/facebookresearch/habitat-sim/tree/main/src/esp/gfx_batch) module in Habitat-sim.
* `shaders:` used by `gfx_batch` (and should probably be moved inside)
* `cuda_tensor_helper:` a tiny Python extension module that provides helpers to convert CUDA memory pointers to PyTorch tensors. It's separate from `habitat_ml_renderer` because it must be [built](cuda_tensor_helper/setup.py) using a special PyTorch-provided CUDAExtension helper.
* `magnum_root:` where `build_magnum.sh` clones, builds, and installs Magnum repos.
* `data:` a folder for runtime data like test 3D models.
there).

# Building

```
# install some conda/mamba items
mamba install cmake pybind11

# install pytorch with CUDA. We don't require a specific CUDA version. See https://pytorch.org/get-started/locally/ for latest instructions.
mamba install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia

# install CUDA toolkit (not shown). See https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html .

# make sure CMake can find your CUDA install, including nvcc. We don't require a specific CUDA version. 
export PATH="/usr/local/cuda-12.3/bin:$PATH"
which nvcc

# install pip requirements
pip install requirements.txt

# build/install cuda_tensor_helper
cd cuda_tensor_helper
pip install -e .
cd ../

# build magnum. Optional args: --debug and --clean.
./build_magnum.sh

# build habitat_ml_renderer extension. Optional args: --debug and --clean.
./build.sh

# run test
python test.py
```

# Magnum third-party graphics library

[Magnum](https://magnum.graphics/) is a graphics library. The Habitat team often works directly with Magnum's developer, [mosra](https://github.com/mosra/).

There are several ways to build/install Magnum. For this project, we do a [manual build](https://doc.magnum.graphics/magnum/building.html#building-manual) using our custom `build_magnum.sh` script. This script requires customization for our project based on the particular Magnum components we use, for example:

* We currently include `<Magnum/GL/OpenGLTester.h>` in `gfx_batch` source files.
* This requires customization of `gfx_batch/CMakeLists.txt`. See `find_package(Magnum ... OpenGLTester)` and `target_link_libraries(... Magnum::OpenGLTester ...)`.
* This in turn requires customization of `magnum_build.sh`. See `-DMAGNUM_WITH_OPENGLTESTER=ON`.

At a high level, this script is cloning magnum source repos to `./magnum_root`, building `.so` library files and other binaries, and then "installing" (copying) Magnum headers and library files to `./magnum_root/install_root` so that our `gfx_batch` library can compile and link with them. See also our main [`CMakeLists.txt`](./CMakeLists.txt)'s usage of `-DCMAKE_INSTALL_PREFIX=../magnum_root/install_root` to find this install location.


