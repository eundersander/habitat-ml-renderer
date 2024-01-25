

import torch  # isort:skip # noqa: F401  must import torch before importing cuda_tensor_helper

import cuda_tensor_helper
import habitat_ml_renderer as hmr
import numpy as np
import pyrr

def perspective_projection_matrix(fov_y, aspect_ratio, near, far):
    """Create a perspective projection matrix.
    Args:
        fov_y (float): The vertical field of view, in radians.
        aspect_ratio (float): The aspect ratio, which is the width of the viewport divided by the height.
        near (float): The distance to the near clipping plane.
        far (float): The distance to the far clipping plane.
    Returns:
        np.ndarray: A 4x4 perspective projection matrix.
    """
    f = 1.0 / np.tan(fov_y / 2.0)
    mat = np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
        [0, 0, -1, 0]
    ])
    return mat.T


def look_at(eye, target, up):
    backward = (eye - target)
    backward /= np.linalg.norm(backward)
    right = np.cross(up, backward)
    right /= np.linalg.norm(right)
    realUp = np.cross(backward, right)
    return np.array([np.append(right, 0), np.append(realUp, 0), np.append(backward, 0), np.append(eye, 1)])


def main():

  num_envs = 8
  image_width = 512
  image_height = 512

  # todo: how to specify GPU for RendererStandalone
  renderer = hmr.RendererStandalone(
    image_width=image_width,
    image_height=image_height,
    num_envs=num_envs)

  renderer.add_file("data/Duck.glb", "Duck", whole=True)

  instances_by_scene = [[]] * num_envs
  for scene_id in range(num_envs):
    instances_by_scene[scene_id].append(renderer.add_node_hierarchy(scene_id, "Duck"))

  SIMULATOR_GPU_ID = 0
  
  # construct tensors to wrap the color and depth buffers provided by the renderer
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

  projections = []
  views = []
  for scene_id in range(num_envs):
    aspect_ratio = image_width / image_height
    fov_y = np.radians(90)
    proj = perspective_projection_matrix(fov_y=fov_y, aspect_ratio=aspect_ratio, near=0.001, far=100.0)
    projections.append(proj)

    # vary the camera eye x across envs so that each env output image is slightly different
    eye = np.array([-3.0 + scene_id * 0.5, 0.0, -3.0])
    target = np.array([0.0, 0.0, 0.0])
    up = np.array([0.0, -1.0, 0.0])
    view = np.linalg.inv(look_at(eye, target, up))
    views.append(view)

  batch_projection = np.stack(projections)
  batch_view = np.stack(views)
  renderer.update_camera(batch_projection, batch_view)

  renderer.draw()

  # Always call this after drawing to update the color and depth tensors. Todo: make
  # a more intuitive interface.
  renderer.rgba()
  renderer.depth()


  from PIL import Image
  tensor = color.cpu()
  images = [Image.fromarray((tensor[i].numpy()).astype('uint8')) for i in range(tensor.shape[0])]
  combined_image = Image.fromarray(np.vstack([np.array(img) for img in images]))
  combined_image.save('output_color.png')

  tensor = depth.cpu()
  images = [Image.fromarray((tensor[i].numpy() * 255).astype('uint8'), 'L') for i in range(tensor.shape[0])]
  # Concatenate the images vertically
  combined_image = Image.fromarray(np.vstack([np.array(img) for img in images]), 'L')
  # Save the combined image to a file
  combined_image.save('output_depth.png')

  print("test.py completed without error!")

if __name__ == "__main__":
  main()