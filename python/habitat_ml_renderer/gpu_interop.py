"""
GPU interop utilities using CuPy for OpenGL-CUDA interoperability.

This module replaces the old cuda_tensor_helper C++ extension with a pure 
Python implementation using CuPy for zero-copy GL buffer to PyTorch tensor conversion.
"""

import torch
from typing import Tuple, Optional
import warnings

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None


class GLTensorBridge:
    """
    CuPy-based bridge for converting OpenGL buffers to PyTorch tensors.
    
    This provides zero-copy GPU-to-GPU transfer from OpenGL framebuffers
    to PyTorch tensors, replacing the functionality of cuda_tensor_helper.
    """
    
    def __init__(self, cuda_device: int = 0):
        """
        Initialize the GL-CUDA bridge.
        
        Args:
            cuda_device: CUDA device ID to use
            
        Raises:
            RuntimeError: If CuPy is not available or CUDA is not accessible
        """
        if not CUPY_AVAILABLE:
            raise RuntimeError(
                "CuPy is not available. Install with: pip install cupy-cuda12x"
            )
        
        self.cuda_device = cuda_device
        
        # Verify CUDA is accessible
        try:
            with cp.cuda.Device(cuda_device):
                device_count = cp.cuda.runtime.getDeviceCount()
                if device_count == 0:
                    raise RuntimeError("No CUDA devices found")
        except Exception as e:
            raise RuntimeError(f"CUDA initialization failed: {e}")
    
    def gl_buffer_to_color_tensor(self, 
                                  gl_buffer_id: int, 
                                  batch_size: int,
                                  resolution: Tuple[int, int]) -> torch.Tensor:
        """
        Convert OpenGL color buffer to PyTorch tensor.
        
        Args:
            gl_buffer_id: OpenGL buffer object ID
            batch_size: Number of environments/scenes
            resolution: (height, width) of each image
            
        Returns:
            PyTorch tensor of shape (batch_size, height, width, 4) with RGBA data
        """
        with cp.cuda.Device(self.cuda_device):
            with cp.cuda.gl.GLMemory(gl_buffer_id) as gl_mem:
                # RGBA format: 4 channels
                shape = (batch_size, resolution[0], resolution[1], 4)
                cupy_array = cp.asarray(gl_mem, dtype=cp.uint8).reshape(shape)
                
                # Zero-copy conversion to PyTorch
                return torch.as_tensor(cupy_array, device=f'cuda:{self.cuda_device}')
    
    def gl_buffer_to_depth_tensor(self, 
                                  gl_buffer_id: int,
                                  batch_size: int, 
                                  resolution: Tuple[int, int]) -> torch.Tensor:
        """
        Convert OpenGL depth buffer to PyTorch tensor.
        
        Args:
            gl_buffer_id: OpenGL buffer object ID
            batch_size: Number of environments/scenes
            resolution: (height, width) of each image
            
        Returns:
            PyTorch tensor of shape (batch_size, height, width) with depth data
        """
        with cp.cuda.Device(self.cuda_device):
            with cp.cuda.gl.GLMemory(gl_buffer_id) as gl_mem:
                # Depth format: single channel float32
                shape = (batch_size, resolution[0], resolution[1])
                cupy_array = cp.asarray(gl_mem, dtype=cp.float32).reshape(shape)
                
                # Zero-copy conversion to PyTorch
                return torch.as_tensor(cupy_array, device=f'cuda:{self.cuda_device}')
    
    def check_gpu_available(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            with cp.cuda.Device(self.cuda_device):
                cp.cuda.runtime.getDeviceCount()
                return True
        except:
            return False


def create_bridge(cuda_device: int = 0) -> Optional[GLTensorBridge]:
    """
    Factory function to create a GL tensor bridge with graceful fallback.
    
    Args:
        cuda_device: CUDA device ID
        
    Returns:
        GLTensorBridge instance or None if GPU not available
    """
    try:
        return GLTensorBridge(cuda_device)
    except RuntimeError as e:
        warnings.warn(f"GPU bridge creation failed: {e}")
        return None


# Legacy compatibility functions for migration from cuda_tensor_helper
def make_color_tensor(ptr_capsule, dev_id: int, batch_size: int, resolution: Tuple[int, int]) -> torch.Tensor:
    """
    Legacy compatibility function for cuda_tensor_helper.make_color_tensor().
    
    Note: This is a transitional function. The new approach uses GLTensorBridge
    with actual GL buffer IDs instead of raw pointers.
    """
    warnings.warn(
        "make_color_tensor is deprecated. Use GLTensorBridge.gl_buffer_to_color_tensor() instead.",
        DeprecationWarning
    )
    # This would need to be implemented based on how ptr_capsule maps to GL buffer ID
    raise NotImplementedError("Use GLTensorBridge directly for new code")


def make_depth_tensor(ptr_capsule, dev_id: int, batch_size: int, resolution: Tuple[int, int]) -> torch.Tensor:
    """
    Legacy compatibility function for cuda_tensor_helper.make_depth_tensor().
    
    Note: This is a transitional function. The new approach uses GLTensorBridge
    with actual GL buffer IDs instead of raw pointers.
    """
    warnings.warn(
        "make_depth_tensor is deprecated. Use GLTensorBridge.gl_buffer_to_depth_tensor() instead.",
        DeprecationWarning
    )
    # This would need to be implemented based on how ptr_capsule maps to GL buffer ID
    raise NotImplementedError("Use GLTensorBridge directly for new code")