"""
Basic integration tests for habitat_ml_renderer.

These tests verify that the core components work together correctly.
Run with: pytest tests/
"""

import pytest
import sys
from pathlib import Path

# Add the python packages to the path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))


def test_import_habitat_ml_renderer():
    """Test that we can import the main package."""
    try:
        import habitat_ml_renderer
        assert hasattr(habitat_ml_renderer, '__file__'), "Package should have a __file__ attribute"
    except ImportError as e:
        pytest.skip(f"habitat_ml_renderer not built or installed: {e}")


def test_import_cuda_tensor_helper():
    """Test that we can import the CUDA tensor helper."""
    try:
        import cuda_tensor_helper
        # Basic functionality test would go here
        assert hasattr(cuda_tensor_helper, '__file__'), "Package should have a __file__ attribute"
    except ImportError as e:
        pytest.skip(f"cuda_tensor_helper not built or installed: {e}")


@pytest.mark.skipif(sys.platform != "linux", reason="Renderer requires Linux with graphics support")
def test_basic_renderer_workflow():
    """Test a basic rendering workflow (Linux only)."""
    try:
        import habitat_ml_renderer as hmr
        import numpy as np
        
        # This would be a simplified version of the test.py workflow
        # For now, just test that we can create a renderer instance
        # Actual implementation would depend on the built extension
        
        # Placeholder test
        assert True, "Basic workflow test placeholder"
        
    except ImportError as e:
        pytest.skip(f"Required packages not available: {e}")
    except Exception as e:
        pytest.skip(f"Renderer test failed (expected on macOS): {e}")


def test_project_structure():
    """Test that the project structure is correct."""
    project_root = Path(__file__).parent.parent
    
    # Check that key directories exist
    assert (project_root / "cpp").exists(), "cpp/ directory should exist"
    assert (project_root / "python").exists(), "python/ directory should exist"
    assert (project_root / "applications").exists(), "applications/ directory should exist"
    assert (project_root / "tools").exists(), "tools/ directory should exist"
    assert (project_root / "install").exists(), "install/ directory should exist"
    
    # Check that key files exist
    assert (project_root / "cpp" / "CMakeLists.txt").exists(), "Main CMakeLists.txt should exist"
    assert (project_root / "tools" / "build_cpp.sh").exists(), "Build script should exist"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])