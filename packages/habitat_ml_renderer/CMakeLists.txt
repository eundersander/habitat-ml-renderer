pybind11_add_module(
  habitat_ml_renderer
  habitat_ml_renderer.cpp
)
target_link_libraries(
  habitat_ml_renderer
  PUBLIC gfx_batch
)
