import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'escort_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='Autonomous escort robot simulation (ROS 2 Jazzy + Gazebo)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'target_simulator = escort_robot.target_simulator:main',
            'escort_controller = escort_robot.escort_controller:main',
        ],
    },
)
