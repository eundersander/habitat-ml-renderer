# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the CC-BY-NC license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import setup, Extension
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
import os

setup(
    name="cuda_tensor_helper",
    ext_modules=[
        CUDAExtension(
            name="cuda_tensor_helper",
            sources=["cuda_tensor_helper.cpp"],
            extra_compile_args=[],
            extra_link_args=[],
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
