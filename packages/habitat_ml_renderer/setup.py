import os
import pathlib
import subprocess
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name)).parent.absolute()
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ]

        build_args = []

        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        # Run CMake configure at the *repo root*
        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args,
            cwd=build_temp,
        )

        # Build just the habitat_ml_renderer target
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "habitat_ml_renderer"] + build_args,
            cwd=build_temp,
        )

setup(
    name="habitat-ml-renderer",
    version="0.1",
    ext_modules=[
        # Important: point at repo root, not package folder
        CMakeExtension("habitat_ml_renderer", sourcedir=os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    ],
    cmdclass={"build_ext": CMakeBuild},
)
