# Installation
```
mamba install python==3.10 cmake

# habitat_ml_renderer
mamba install pybind11 pytorch pytorch-cuda=12.4 -c pytorch -c nvidia
pip install -e packages/cuda_tensor_helper_src --no-build-isolation
./build_magnum.sh
pip install -e packages/habitat_ml_renderer
# optional: test
python packages/habitat_ml_renderer/tests/test.py

# mochi
./build_mochi.sh
pip install ./mochi/python

# mochi_gym
pip install -e mochi/mochi_gym

# tbd
pip install -e packages/tbd

# data
cd data
git clone https://huggingface.co/datasets/ai-habitat/mochi_vr_data.git

# test mochi, mochi_gym, and tbd
python examples/envs/run_allegro_grasp_env.py
```