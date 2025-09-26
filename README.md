# Habitat-ml-renderer

A python extension module for loading 3D scenes, batch-rendering them via OpenGL, and exposing the resulting batch of images as a PyTorch CUDA tensor (RGB and/or depth). We target ML applications, specifically [batch rollout generation](#batch-rollouts) in simulation for e.g. reinforcement learning. 

![output_color](https://github.com/eundersander/habitat-ml-renderer/assets/6557808/6fe7aa5c-8e0a-4d04-8937-67352533af0d)
![output_depth](https://github.com/eundersander/habitat-ml-renderer/assets/6557808/ef2311a9-748b-47c6-afff-b3d7c7b9ba0a)

*Above, example output images from [test.py](./test.py).*

This project is based on the [`esp/gfx_batch`](https://github.com/facebookresearch/habitat-sim/tree/main/src/esp/gfx_batch) library inside Habitat-sim, but it aims to have minimal dependencies (mostly Magnum, PyTorch, and CUDA Toolkit so far). This project may eventually be moved into the Habitat-sim repo.

**Contents**
- [Habitat-ml-renderer](#habitat-ml-renderer)
- [Todo](#todo)
- [Directory structure](#directory-structure)
- [Building and testing](#building-and-testing)
- [System overview](#system-overview)
  - [Rendering 3D scenes](#rendering-3d-scenes)
  - [Batch rollouts](#batch-rollouts)
- [Magnum third-party graphics library](#magnum-third-party-graphics-library)

# Todo
* Flesh out our [python API](./habitat_ml_renderer/habitat_ml_renderer.cpp) and [test.py](./test.py)
    * Fix the unintuitive python interfaces for creating image tensors and updating them after drawing.
        * Currently, the confusingly-named `rgba` is used for both creating and updating.
        * The C++ function `Renderer::colorCudaBufferDevicePointer` is also misleading because it suggests you only need to call it once at startup; you actually have to call this after every draw.
        * We need to update both the RGB and depth interfaces.
    * Update instances between draws using `Renderer::transformations` (add bindings as necessary); render multiple batch frames.
* Lighting and shading polish
    * The current draw test is "flat shading" (all surfaces at maximum brightness). RendererStandalone should support Phong shading, too, but I'm not sure how to enable it. It may be as simple as adding one or more lights. RendererStandalone already has an interface for adding lights. Experiment with this (add bindings as necessary).
    * Experiment with HBAO effect for adding soft shadows.
* Avoid code duplication with Habitat-sim
    * Currently, the `gfx_batch` is (mostly) copy-pasted from Habitat-sim [`esp/gfx_batch`](https://github.com/facebookresearch/habitat-sim/tree/main/src/esp/gfx_batch). In the long term, this will be a problem as the Habitat team and Mosra start pushing new fixes and improvements there. We need to find a way for Habitat-sim and Habitat-ml-renderer to share `gfx_batch`. Habitat-ml-renderer should potentially be moved into the Habitat-sim repo, although it should remain a standalone project with minimal dependencies (e.g. no dependency on the Habitat-sim codebase).
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
* `cuda_tensor_helper:` a tiny Python extension module that provides helpers to convert CUDA memory pointers to PyTorch tensors. It's separate from `habitat_ml_renderer` because it must be [built](cuda_tensor_helper/setup.py) using a special PyTorch-provided CUDAExtension helper which tends to not give us enough control over the build settings (e.g. there is no CMakeLists.txt). 
* `magnum_root:` where `build_magnum.sh` clones, builds, and installs Magnum repos.
* `data:` a folder for runtime data like test 3D models, including `Duck.glb`.
there).

# Building and testing

```
# install some conda/mamba items
mamba install python==3.10 cmake pybind11

# install pytorch with CUDA. We don't require a specific CUDA version. See https://pytorch.org/get-started/locally/ for latest instructions.
mamba install pytorch pytorch-cuda=12.4 -c pytorch -c nvidia

# install CUDA toolkit (not shown). See https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html .

# make sure CMake can find your CUDA install, including nvcc. We don't require a specific CUDA version. On some machines you may need to do e.g. `export PATH="/usr/local/cuda-12.3/bin:$PATH"`.
which nvcc

# install pip requirements
pip install -r requirements.txt

# build/install cuda_tensor_helper
cd cuda_tensor_helper_src
pip install -e . --no-build-isolation
cd ../

# build magnum. Optional args: --debug and --clean.
./build_magnum.sh

# build habitat_ml_renderer extension. Optional args: --debug and --clean.
./build.sh

# run test
python test.py
```

# System overview

## Rendering 3D scenes

A simulated 3D scene (aka environment) generally consists of movable rigid objects: e.g. building walls, floors, furniture, and articulated robots. (Some simulators also support soft bodies, cloth, fluids, or other non-rigid elements, but `Habitat-ml-renderer` only supports rendering rigid objects.)

To render a batch of scenes in `Habitat-ml-renderer`:
1. Load 3D model files. See `add_file` usage in [test.py](./test.py).
2. Instantiatate a 3D model (aka instance) for each rigid object in each scene. See `add_node_hierarchy`.
3. Update instance poses as the scene states change (e.g. stepping your physics simulation). See `RendererStandalone::transformations`.
4. Update the camera for each scene. See `update_camera`.
5. Draw all scenes to produce output color and depth images. See `draw`, `rgba`, and `depth`.

## Batch rollouts

We target ML applications, specifically "batch rollout generation" in simulation for e.g. reinforcement learning. A typical batch rollout step consists of:
1. **Vision-based policy:** For example, a PyTorch CNN model. Run batch inference for your vision-based policy to compute RL agent actions, using image output from the previous step as input to the policy. 
2. **Physics simulation:** For example, [Habitat-sim](https://github.com/facebookresearch/habitat-sim) or [Isaac Sim](https://developer.nvidia.com/isaac-sim). Step the physics simulation for multiple environments. This can be multiple simulator instances stepping in parallel or a single *batch* simulator like Isaac Sim. The simulator output should be an updated list of poses (position and rotation) for the rigid objects in each 3D scene.
3. **Rendering:** Batch-render the scene states to a single batch output RGB (and/or depth) image tensor. `Habitat-ml-renderer` provides exactly this piece!

# Magnum third-party graphics library

[Magnum](https://magnum.graphics/) is a graphics library where much of `Habitat-ml-renderer`'s core renderer is implemented. The Habitat team often works directly with Magnum's developer, [mosra](https://github.com/mosra/). In this section, we document how Magnum is integrated into the project's build system.

There are several ways to build/install Magnum. For this project, we do a [manual build](https://doc.magnum.graphics/magnum/building.html#building-manual) using our custom `build_magnum.sh` script. This script requires customization for our project based on the particular Magnum components we use, for example:

* We currently include `<Magnum/GL/OpenGLTester.h>` in `gfx_batch` source files.
* This requires customization of `gfx_batch/CMakeLists.txt`. See `find_package(Magnum ... OpenGLTester)` and `target_link_libraries(... Magnum::OpenGLTester ...)`.
* This in turn requires customization of `magnum_build.sh`. See `-DMAGNUM_WITH_OPENGLTESTER=ON`.

At a high level, this script is cloning magnum source repos to `./magnum_root`, building `.so` library files and other binaries, and then "installing" (copying) Magnum headers and library files to `./magnum_root/install_root` so that our `gfx_batch` library can compile and link with them. See also our main [`CMakeLists.txt`](./CMakeLists.txt)'s usage of `-DCMAKE_INSTALL_PREFIX=../magnum_root/install_root` to find this install location.


