# C++ Integration Tests

# Add the integration test executable
add_executable(test_integration test_integration.cpp)

# Link against gfx_batch library when it's available
if(TARGET gfx_batch)
    target_link_libraries(test_integration PRIVATE gfx_batch)
endif()

# Install the test executable
install(TARGETS test_integration DESTINATION bin)