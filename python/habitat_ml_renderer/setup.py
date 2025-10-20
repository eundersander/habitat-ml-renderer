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
    """Create a symlink from the package to the built extension in install/"""
    # Path to the built extension in install/
    install_dir = pathlib.Path(__file__).parent.parent.parent / "install" / "lib"
    extension_file = install_dir / "habitat_ml_renderer.so"
    
    # Path where the symlink should be created (in the Python package)
    package_dir = pathlib.Path(__file__).parent / "habitat_ml_renderer" 
    package_dir.mkdir(exist_ok=True)
    symlink_target = package_dir / "habitat_ml_renderer.so"
    
    # Remove existing symlink/file if it exists
    if symlink_target.exists() or symlink_target.is_symlink():
        symlink_target.unlink()
    
    # Create the symlink if the extension exists
    if extension_file.exists():
        symlink_target.symlink_to(extension_file.resolve())
        print(f"Created symlink: {symlink_target} -> {extension_file}")
    else:
        print(f"Warning: Extension not found at {extension_file}")
        print("Make sure to run tools/build_cpp.sh first!")


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
