# Escort Robot Simulation (ROS 2 Jazzy + Gazebo)

An autonomous escort robot that follows a target while avoiding obstacles,
simulated in Gazebo and controlled through ROS 2.

```
target_simulator  --/target_position-->  escort_controller  --/cmd_vel-->  ros_gz_bridge --> Gazebo
                                                 ^                                              |
                                                 |-----------  /odom , /scan  <----------------|
```

This repo is a ready-to-build ROS 2 workspace. The package lives in
[`src/escort_robot`](src/escort_robot).

---

## Requirements (on the machine that runs it)

- **WSL (Ubuntu 24.04) or native Ubuntu 24.04**
- **ROS 2 Jazzy** installed at `/opt/ros/jazzy`
- **Gazebo** (installed automatically by `build.sh` via `ros-jazzy-ros-gz`)

Quick check that the base is in place:

```bash
echo $ROS_DISTRO      # should print: jazzy
gz sim --version      # should print a Gazebo version
```

> Windows note: ROS 2 + Gazebo do **not** run on plain Windows. Use WSL
> (or a real Ubuntu machine). GUI windows work through WSLg automatically.

---

## Run it in 4 steps

Open a WSL / Ubuntu terminal and:

```bash
# 1. Clone the repo as your workspace
git clone <REPO_URL> ~/escort_ws

# 2. Build it (installs Gazebo too; asks for your sudo password once)
cd ~/escort_ws
./build.sh

# 3. Run the full simulation
./run.sh
```

That's it. Gazebo opens with the robot, the target (tall cylinder) and the
obstacle (box). The robot drives toward the target, steers around the
obstacle, and stops about **1 metre** from the target.

If `./build.sh` says *permission denied*, run it with bash instead:

```bash
bash build.sh
bash run.sh
```

---

## Checking that it works

In a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/escort_ws/install/setup.bash

ros2 topic list
# expect: /cmd_vel  /odom  /scan  /imu  /joint_states  /target_position  /clock

ros2 topic echo /imu                 # raw IMU: angular velocity + linear accel
ros2 topic echo /joint_states        # per-wheel angle + velocity (encoders)

ros2 topic echo /target_position     # data: [5.0, 0.0]
ros2 topic echo /cmd_vel             # linear/angular velocity commands
```

See the full node/topic graph:

```bash
rqt_graph
```

---

## Running pieces individually (optional)

```bash
source /opt/ros/jazzy/setup.bash
source ~/escort_ws/install/setup.bash

# just the Gazebo world
gz sim src/escort_robot/worlds/escort_world.sdf

# just the target publisher
ros2 run escort_robot target_simulator

# just the controller
ros2 run escort_robot escort_controller
```

---

## What's inside

| File | Purpose |
|------|---------|
| `src/escort_robot/escort_robot/target_simulator.py` | Publishes the target position on `/target_position`. |
| `src/escort_robot/escort_robot/escort_controller.py` | Follows the target, avoids obstacles, publishes `/cmd_vel`. |
| `src/escort_robot/worlds/escort_world.sdf` | Gazebo world: ground, robot (diff-drive + LiDAR + IMU + wheel joint states), target, obstacle. |
| `src/escort_robot/config/bridge.yaml` | ROS <-> Gazebo topic bridge. |
| `src/escort_robot/launch/escort_sim.launch.py` | Launches Gazebo + bridge + both nodes together. |
| `build.sh` / `run.sh` | Convenience scripts. |

---

## Later: swapping the simulator for real hardware

The controller only cares about `/target_position` and the sensor topics, so
the simulator can be replaced without touching `escort_controller.py`:

```
Now:    target_simulator.py  -> /target_position -> escort_controller -> /cmd_vel -> Gazebo
Later:  camera + OpenCV      -> /target_position -> escort_controller -> /cmd_vel -> ESP32 / motors
```
