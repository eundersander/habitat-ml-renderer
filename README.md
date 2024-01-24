

# `gfx_batch`

The [`gfx_batch`](./gfx_batch) library here is based on the [`esp/gfx_batch`](https://github.com/facebookresearch/habitat-sim/tree/main/src/esp/gfx_batch) module in Habitat-sim.

# Magnum third-party graphics library

[Magnum](https://magnum.graphics/) is a graphics library. The Habitat team often works directly with Magnum's developer, [mosra](https://github.com/mosra/).

There are several ways to build/install Magnum. For this project, we do a [manual build](https://doc.magnum.graphics/magnum/building.html#building-manual) using our custom `build_magnum.sh` script. This script requires customization for our project based on the particular Magnum components we use, for example:

* We currently include `<Magnum/GL/OpenGLTester.h>` in `gfx_batch` source files.
* This requires customization of `gfx_batch/CMakeLists.txt`. See `find_package(Magnum ... OpenGLTester)` and `target_link_libraries(... Magnum::OpenGLTester ...)`.
* This in turn requires customization of `magnum_build.sh`. See `-DMAGNUM_WITH_OPENGLTESTER=ON`.

At a high level, this script is cloning magnum source repos to `./external`, building `.so` library files and other binaries, and then "installing" (copying) Magnum headers and library files to `./external/install_root` so that our `gfx_batch` library can compile and link with them. See also our main [`CMakeLists.txt`](./CMakeLists.txt)'s usage of `-DCMAKE_INSTALL_PREFIX=../external/install_root` to find this install location.

# Old stuff below


mamba install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia

cd bps_pytorch
pip install -e .
cd ../


after this installs, find the location of your pybind11 install!
something like /home/your_username/mambaforge/envs/your_conda_env_name/lib/python3.11/site-packages/pybind11
pip install pybind11


-DCMAKE_PREFIX_PATH=/path/to/pybind11

