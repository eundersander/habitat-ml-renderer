pybind11_add_module(
  habitat_ml_renderer_python
  Bindings.cpp
)
target_link_libraries(
  habitat_ml_renderer_python
  PUBLIC gfx_batch
)
