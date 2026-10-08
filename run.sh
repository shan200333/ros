#!/usr/bin/env bash
#
# Run the full escort simulation.
#   cd ~/escort_ws && ./run.sh
#
set -e

# Move into the workspace root (folder this script lives in).
cd "$(dirname "$0")"

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch escort_robot escort_sim.launch.py
