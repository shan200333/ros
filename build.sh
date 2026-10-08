#!/usr/bin/env bash
#
# One-time build. Run this once after cloning.
#   cd ~/escort_ws && ./build.sh
#
set -e

# Move into the workspace root (folder this script lives in).
cd "$(dirname "$0")"

echo "==> Sourcing ROS 2 Jazzy"
source /opt/ros/jazzy/setup.bash

echo "==> Installing Gazebo + ros_gz (needs your sudo password)"
sudo apt-get update
sudo apt-get install -y ros-jazzy-ros-gz

echo "==> Resolving dependencies with rosdep (best effort)"
rosdep install --from-paths src --ignore-src -r -y || true

echo "==> Building with colcon"
colcon build --symlink-install

echo ""
echo "Build complete."
echo "Now run the simulation with:   ./run.sh"
