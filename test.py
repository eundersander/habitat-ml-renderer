

import torch  # isort:skip # noqa: F401  must import torch before importing cuda_tensor_helper

import cuda_tensor_helper
import habitat_ml_renderer as hmr


def main():

  num_envs = 16
  image_width = 256
  image_height = 192

  # todo: how to specify GPU for RendererStandalone
  renderer = hmr.RendererStandalone(
    image_width=image_width,
    image_height=image_height,
    num_envs=num_envs)

  renderer.add_file("data/Duck.glb", "Duck", whole=True)

  SIMULATOR_GPU_ID = 0
  
  color = cuda_tensor_helper.make_color_tensor(
    renderer.rgba(),
    SIMULATOR_GPU_ID,
    num_envs,
    [image_height, image_width],
  )

  depth = cuda_tensor_helper.make_depth_tensor(
    renderer.depth(),
    SIMULATOR_GPU_ID,
    num_envs,
    [image_height, image_width],
  )

  renderer.draw()

  # call this again to update tensor
  renderer.rgba()
  renderer.depth()

  print("test.py completed without error!")

if __name__ == "__main__":
  main()