#!/usr/bin/env python3
"""
Integration test for habitat_ml_renderer using CuPy for GPU interop.

This replaces the old cuda_tensor_helper-based test with a pure CuPy approach.
"""

import torch  # isort:skip # noqa: F401  must import torch before importing cupy
import cupy as cp
import habitat_ml_renderer as hmr
import numpy as np
from typing import Tuple
import sys
from pathlib import Path

# Add the python packages to the path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))


class CupyRendererBridge:
    """CuPy-based bridge for GL-CUDA interop, replacing cuda_tensor_helper"""
    
    def __init__(self, cuda_device: int = 0):
        self.cuda_device = cuda_device
        
    def gl_buffer_to_color_tensor(self, 
                                  gl_buffer_id: int, 
                                  batch_size: int,
                                  resolution: Tuple[int, int]) -> torch.Tensor:
        """Convert GL color buffer to PyTorch tensor using CuPy"""
        
        with cp.cuda.Device(self.cuda_device):
            # Map GL buffer with CuPy
            with cp.cuda.gl.GLMemory(gl_buffer_id) as gl_mem:
                # Create CuPy array view (RGBA format)
                shape = (batch_size, resolution[0], resolution[1], 4)
                cupy_array = cp.asarray(gl_mem, dtype=cp.uint8).reshape(shape)
                
                # Zero-copy conversion to PyTorch tensor
                return torch.as_tensor(cupy_array, device=f'cuda:{self.cuda_device}')
        
    def gl_buffer_to_depth_tensor(self, 
                                  gl_buffer_id: int,
                                  batch_size: int, 
                                  resolution: Tuple[int, int]) -> torch.Tensor:
        """Convert GL depth buffer to PyTorch tensor using CuPy"""
        
        with cp.cuda.Device(self.cuda_device):
            with cp.cuda.gl.GLMemory(gl_buffer_id) as gl_mem:
                # Create CuPy array view (depth format)
                shape = (batch_size, resolution[0], resolution[1])
                cupy_array = cp.asarray(gl_mem, dtype=cp.float32).reshape(shape)
                
                # Zero-copy conversion to PyTorch tensor
                return torch.as_tensor(cupy_array, device=f'cuda:{self.cuda_device}')


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
    """Helper for creating a view (camera) matrix"""
    backward = (eye - target)
    backward /= np.linalg.norm(backward)
    right = np.cross(up, backward)
    right /= np.linalg.norm(right)
    realUp = np.cross(backward, right)
    return np.array([np.append(right, 0), np.append(realUp, 0), np.append(backward, 0), np.append(eye, 1)])


def test_habitat_ml_renderer_basic():
    """Test basic rendering functionality with CuPy interop"""
    
    print("=== Testing Habitat ML Renderer with CuPy ===")
    
    # Test parameters
    num_envs = 5
    image_width = 192
    image_height = 256
    SIMULATOR_GPU_ID = 0

    # Check if CuPy and CUDA are available
    try:
        device_count = cp.cuda.runtime.getDeviceCount()
        print(f"✓ CUDA devices available: {device_count}")
        if device_count == 0:
            print("⚠ No CUDA devices - skipping GPU tests")
            return
    except Exception as e:
        print(f"⚠ CUDA not available: {e} - skipping GPU tests")
        return

    # Create renderer
    print("Creating renderer...")
    renderer = hmr.RendererStandalone(
        image_width=image_width,
        image_height=image_height,
        num_envs=num_envs)

    # Add 3D model files
    print("Loading 3D assets...")
    renderer.add_file("library_data/test_assets/objects/Duck.glb", "Duck", whole=True)

    # Construct scenes
    print("Setting up scenes...")
    instances_by_scene = [[]] * num_envs
    for scene_id in range(num_envs):
        instances_by_scene[scene_id].append(renderer.add_node_hierarchy(scene_id, "Duck"))

    # Set up cameras
    print("Configuring cameras...")
    projections = []
    views = []
    for scene_id in range(num_envs):
        aspect_ratio = image_width / image_height
        fov_y = np.radians(70)
        proj = perspective_projection_matrix(fov_y=fov_y, aspect_ratio=aspect_ratio, near=0.4, far=10.0)
        projections.append(proj)

        # Vary camera position across envs
        eye = np.array([2.0, 1.0, -3.5 + scene_id * 2.0])
        target = np.array([0.0, 0.5, 0.0])
        up = np.array([0.0, -1.0, 0.0])
        view = np.linalg.inv(look_at(eye, target, up))
        views.append(view)

    batch_projection = np.stack(projections)
    batch_view = np.stack(views)
    renderer.update_camera(batch_projection, batch_view)

    # Render
    print("Rendering...")
    renderer.draw()

    # Get GPU tensors using existing CUDA interface (transitional)
    print("Converting CUDA buffers to PyTorch tensors using CuPy...")
    
    # Get CUDA device pointers from renderer
    color_ptr_capsule = renderer.rgba()
    depth_ptr_capsule = renderer.depth()
    
    # Convert using CuPy instead of cuda_tensor_helper
    color = cupy_capsule_to_tensor(
        color_ptr_capsule,
        SIMULATOR_GPU_ID,
        num_envs,
        (image_height, image_width, 4)  # RGBA
    )
    
    depth = cupy_capsule_to_tensor(
        depth_ptr_capsule,
        SIMULATOR_GPU_ID,
        num_envs,
        (image_height, image_width)  # Single channel
    )
    
    # Verify tensor shapes
    assert color.shape == (num_envs, image_height, image_width, 4), f"Color shape mismatch: {color.shape}"
    assert depth.shape == (num_envs, image_height, image_width), f"Depth shape mismatch: {depth.shape}"
    
    print(f"✓ Color tensor shape: {color.shape}")
    print(f"✓ Depth tensor shape: {depth.shape}")
    print(f"✓ Tensors are on device: {color.device}")

    # Save output images
    print("Saving output images...")
    save_tensor_images(color, depth)

    print("✓ Habitat ML Renderer test completed successfully!")


def cupy_capsule_to_tensor(ptr_capsule, device_id: int, batch_size: int, shape: tuple) -> torch.Tensor:
    """
    Convert PyCapsule containing CUDA pointer to PyTorch tensor using CuPy.
    
    This replaces cuda_tensor_helper functionality using CuPy.
    """
    # Extract raw CUDA pointer from capsule
    cuda_ptr = int(ptr_capsule)
    
    # Create CuPy array from raw pointer
    total_elements = batch_size * np.prod(shape[1:]) if len(shape) > 3 else batch_size * np.prod(shape)
    
    if len(shape) == 4:  # Color: (batch, height, width, channels)
        dtype = cp.uint8
        full_shape = (batch_size,) + shape[1:]
    else:  # Depth: (batch, height, width)
        dtype = cp.float32  
        full_shape = (batch_size,) + shape[1:]
    
    # Create CuPy array from memory pointer
    cupy_array = cp.ndarray(
        shape=full_shape,
        dtype=dtype,
        memptr=cp.cuda.MemoryPointer(
            cp.cuda.memory.UnownedMemory(cuda_ptr, total_elements * dtype().itemsize, None),
            0
        )
    )
    
    # Convert to PyTorch tensor (zero-copy)
    return torch.as_tensor(cupy_array, device=f'cuda:{device_id}')


def save_tensor_images(color_tensor: torch.Tensor, depth_tensor: torch.Tensor):
    """Save tensor data as images for visual verification"""
    try:
        from PIL import Image
        
        # Convert to CPU for saving
        color_cpu = color_tensor.cpu()
        depth_cpu = depth_tensor.cpu()
        
        # Save color images
        images = [Image.fromarray((color_cpu[i].numpy()).astype('uint8')) for i in range(color_cpu.shape[0])]
        combined_image = Image.fromarray(np.hstack([np.array(img) for img in images]))
        combined_image.save('output_color_cupy.png')
        
        # Save depth images
        images = [Image.fromarray((depth_cpu[i].numpy() * 255).astype('uint8'), 'L') for i in range(depth_cpu.shape[0])]
        combined_image = Image.fromarray(np.hstack([np.array(img) for img in images]), 'L')
        combined_image.save('output_depth_cupy.png')
        
        print("✓ Images saved: output_color_cupy.png, output_depth_cupy.png")
        
    except ImportError:
        print("⚠ PIL not available - skipping image save")
    except Exception as e:
        print(f"⚠ Image save failed: {e}")


def test_cupy_pytorch_interop():
    """Test CuPy-PyTorch interoperability"""
    print("=== Testing CuPy-PyTorch Interop ===")
    
    try:
        # Create CuPy array
        cupy_array = cp.array([1, 2, 3, 4, 5], dtype=cp.float32)
        print(f"✓ CuPy array: {cupy_array}")
        
        # Convert to PyTorch (zero-copy)
        torch_tensor = torch.as_tensor(cupy_array, device='cuda')
        print(f"✓ PyTorch tensor: {torch_tensor}")
        
        # Verify they share memory
        cupy_array[0] = 99
        assert torch_tensor[0] == 99, "Memory not shared!"
        print("✓ Zero-copy memory sharing confirmed")
        
        # Convert back
        torch_tensor2 = torch.tensor([6, 7, 8, 9, 10], device='cuda', dtype=torch.float32)
        cupy_array2 = cp.asarray(torch_tensor2)
        print(f"✓ PyTorch→CuPy: {cupy_array2}")
        
    except Exception as e:
        print(f"✗ CuPy-PyTorch interop failed: {e}")
        raise


if __name__ == "__main__":
    test_cupy_pytorch_interop()
    test_habitat_ml_renderer_basic()