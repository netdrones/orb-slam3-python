cmake_minimum_required(VERSION 3.4...3.19)
project(_orb_slam3 LANGUAGES CXX)

add_subdirectory(pybind11)

pybind11_add_module(
  _orb_slam3
  ${CMAKE_CURRENT_LIST_DIR}/orb_slam3/system.cc
)

find_package(Python 3.8 COMPONENTS Interpreter Development REQUIRED)

add_subdirectory(ORB_SLAM3)

include_directories(
  ${PROJECT_SOURCE_DIR}/ORB_SLAM3
  ${PROJECT_SOURCE_DIR}/ORB_SLAM3/include
  ${PROJECT_SOURCE_DIR}/ORB_SLAM3/include/CameraModels
  ${PROJECT_SOURCE_DIR}/ORB_SLAM3/Thirdparty/Sophus
  ${OpenCV_INCLUDE_DIRS}
  ${Pangolin_INCLUDE_DIRS}
)

target_link_libraries(
  _orb_slam3
  PRIVATE ORB_SLAM3
)