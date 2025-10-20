"""
Habitat ML Renderer - High-performance batch rendering for ML applications.

This package provides efficient 3D rendering with GPU acceleration and
seamless integration with PyTorch for machine learning workflows.
"""

# Import main renderer classes when C++ extension is available
try:
    from . import habitat_ml_renderer as _hmr_core
    # Expose main classes
    RendererStandalone = _hmr_core.RendererStandalone
    # Add other classes as they become available
    
except ImportError as e:
    import warnings
    warnings.warn(f"C++ extension not available: {e}")
    # Define stub classes or graceful fallbacks
    RendererStandalone = None

# Import GPU interop utilities
try:
    from .gpu_interop import GLTensorBridge, create_bridge
    GPU_AVAILABLE = True
except ImportError:
    # Graceful fallback when CuPy not available
    GLTensorBridge = None
    create_bridge = None
    GPU_AVAILABLE = False

__version__ = "0.1.0"
__all__ = [
    "RendererStandalone",
    "GLTensorBridge", 
    "create_bridge",
    "GPU_AVAILABLE"
]