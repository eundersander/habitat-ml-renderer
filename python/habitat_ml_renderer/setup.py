"""
Setup script for habitat_ml_renderer Python package.

This package expects the C++ extension to be pre-built and installed 
in the project's install/ directory using the tools/build_cpp.sh script.

Prerequisites:
1. Run tools/build_magnum.sh to build dependencies
2. Run tools/build_cpp.sh to build the C++ extension
3. Then run: pip install -e python/habitat_ml_renderer/
"""

import os
import pathlib
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


def create_symlink_to_extension():
    """Create a symlink from the package to the built extension in lib/"""
    # Path to the built extension in project root lib/
    project_root = pathlib.Path(__file__).parent.parent.parent
    lib_dir = project_root / "lib"
    
    # Look for the actual extension file (name varies by platform/Python version)
    extension_files = list(lib_dir.glob("habitat_ml_renderer*.so"))
    
    if not extension_files:
        print(f"Warning: No habitat_ml_renderer extension found in {lib_dir}")
        print("Make sure to run tools/build_cpp.sh first!")
        return
    
    extension_file = extension_files[0]  # Use the first match
    
    # Path where the symlink should be created (in the Python package)
    package_dir = pathlib.Path(__file__).parent / "habitat_ml_renderer" 
    package_dir.mkdir(exist_ok=True)
    symlink_target = package_dir / "habitat_ml_renderer.so"
    
    # Remove existing symlink/file if it exists
    if symlink_target.exists() or symlink_target.is_symlink():
        symlink_target.unlink()
    
    # Create the symlink
    symlink_target.symlink_to(extension_file.resolve())
    print(f"Created symlink: {symlink_target} -> {extension_file}")


class DevelopCommand(develop):
    """Custom develop command to create symlinks"""
    def run(self):
        create_symlink_to_extension()
        super().run()


class InstallCommand(install):
    """Custom install command to create symlinks"""
    def run(self):
        create_symlink_to_extension()
        super().run()


setup(
    name="habitat-ml-renderer",
    version="0.1.0",
    description="ML-focused batch renderer for Habitat robotics simulations",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies will be specified in requirements.txt
    ],
    cmdclass={
        "develop": DevelopCommand,
        "install": InstallCommand,
    },
    # Include the symlinked .so file in the package
    package_data={
        "habitat_ml_renderer": ["*.so"],
    },
    include_package_data=True,
)
