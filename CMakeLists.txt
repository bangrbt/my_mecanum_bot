cmake_minimum_required(VERSION 3.8)
project(my_mecanum_bot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

# Lệnh cài đặt để ROS 2 copy các thư mục cấu hình vào thư mục install
install(DIRECTORY
  urdf
  meshes
  launch
  config
  rviz
  world
  models
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/teleop_full.py 
  scripts/auto_trajectory.py
  scripts/read_encoder.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()