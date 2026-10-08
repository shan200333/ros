import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('escort_robot')

    world = os.path.join(
        package_share,
        'worlds',
        'escort_world.sdf'
    )

    bridge_config = os.path.join(
        package_share,
        'config',
        'bridge.yaml'
    )

    # Start Gazebo (gz sim) with the world, running (-r).
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'-r {world}'}.items()
    )

    # ROS <-> Gazebo bridge driven by config/bridge.yaml.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    target_simulator = Node(
        package='escort_robot',
        executable='target_simulator',
        output='screen'
    )

    escort_controller = Node(
        package='escort_robot',
        executable='escort_controller',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        bridge,
        target_simulator,
        escort_controller,
    ])
