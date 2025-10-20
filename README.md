# Habitat ML Renderer

A high-performance batch renderer for machine learning and robotics applications.

## Project Structure

```
habitat/
├── install/                    # Built binaries and extensions
├── cpp/                       # All C++ source code
│   ├── CMakeLists.txt        # Root C++ build system
│   ├── libs/gfx_batch/       # Core rendering library
│   ├── extensions/           # Python binding code
│   ├── tests/               # C++ integration tests
│   └── third_party/         # External C++ dependencies
├── python/                   # Python packages
│   ├── habitat_ml_renderer/  # Main Python package
│   └── tbd/                 # Additional utilities
├── applications/            # Team applications
├── tests/                   # Python integration tests
├── tools/                   # Build scripts
└── assets/                  # Test data and assets
```

## Installation

**Prerequisites:**
- Linux system with CUDA support (for full functionality)
- Python 3.10
- CMake
- Mamba/Conda environment

### Setup Development Environment

```bash
# Create and activate mamba environment
mamba create -n habitat python=3.10 cmake
mamba activate habitat

# For Linux with CUDA:
mamba install pybind11 pytorch pytorch-cuda=12.4 cupy -c pytorch -c nvidia -c conda-forge

# For macOS (limited functionality):
mamba install pybind11 pytorch -c pytorch
```

### Build Instructions

```bash
# 1. Build graphics dependencies
./tools/build_magnum.sh

# 2. Build C++ libraries and extensions
./tools/build_cpp.sh

# 3. Install Python packages
pip install -e python/habitat_ml_renderer/

# 4. Optional: Install other packages
pip install -e python/tbd/
```

### Testing

```bash
# Run Python tests
pytest tests/

# Run C++ tests (when built)
./cpp/build/tests/test_integration

# Run integration test with CuPy
python tests/test_habitat_ml_renderer.py
```

## Development Workflow

1. **C++ Changes**: Edit code in `cpp/`, then run `./tools/build_cpp.sh`
2. **Python Changes**: Edit code in `python/`, changes are immediately available
3. **Applications**: Create new applications in `applications/` directory
4. **Tests**: Add tests in the centralized `tests/` directory

## Platform Support

- **Linux**: Full support with CUDA acceleration
- **macOS**: Limited support (no CUDA, graphics may be limited)
- **Windows**: Not currently supported

## Architecture

The project follows a clear separation of concerns:

- **C++ Core** (`cpp/libs/gfx_batch/`): High-performance rendering engine
- **Python Extensions** (`cpp/extensions/`): Python bindings for C++ core
- **Python Packages** (`python/`): High-level Python APIs and utilities
- **Applications** (`applications/`): End-user applications
- **Shared Build** (`install/`): All built artifacts in one location