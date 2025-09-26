from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
import torch, os, sys

torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
conda_lib = os.path.join(os.environ.get("CONDA_PREFIX", ""), "lib")

rpaths = []
for p in (torch_lib, conda_lib):
    if p and os.path.isdir(p):
        rpaths.append(p)

# Fallback to $ORIGIN relative search (works if extension sits near torch/lib)
rpaths.append("$ORIGIN")

# Turn rpaths into linker flags
link_rpaths = [f"-Wl,-rpath,{p}" for p in rpaths]

ext = CUDAExtension(
    name="cuda_tensor_helper",
    sources=["cuda_tensor_helper.cpp"],
    extra_link_args=link_rpaths,
    runtime_library_dirs=[p for p in rpaths if not p.startswith("$")],  # $ORIGIN not accepted here
)

setup(
    name="cuda_tensor_helper",
    ext_modules=[ext],
    cmdclass={"build_ext": BuildExtension},
)
