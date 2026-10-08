import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray


class EscortController(Node):
    """Drives the robot toward the target while avoiding obstacles.

    Inputs:
      /target_position (std_msgs/Float32MultiArray)  -> [x, y]
      /odom            (nav_msgs/Odometry)           -> robot pose
      /scan            (sensor_msgs/LaserScan)       -> obstacles

    Output:
      /cmd_vel         (geometry_msgs/Twist)         -> wheel commands
    """

    def __init__(self):
        super().__init__('escort_controller')

        # Target (from target_simulator / later a person tracker)
        self.target_x = None
        self.target_y = None

        # Robot pose (from odometry)
        self.robot_x = None
        self.robot_y = None
        self.robot_yaw = None

        # Obstacle distances (from LiDAR)
        self.front_distance = float('inf')
        self.left_distance = float('inf')
        self.right_distance = float('inf')

        # Tunable behaviour parameters
        self.stop_distance = 1.0        # stop ~1 m away from the target
        self.obstacle_threshold = 0.65  # treat as blocked within 0.65 m
        self.max_linear = 0.5           # m/s
        self.max_angular = 1.0          # rad/s

        self.create_subscription(
            Float32MultiArray,
            '/target_position',
            self.target_callback,
            10
        )
        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)

    # ------------------------------------------------------------------ #
    # Subscription callbacks
    # ------------------------------------------------------------------ #
    def target_callback(self, msg):
        if len(msg.data) >= 2:
            self.target_x = msg.data[0]
            self.target_y = msg.data[1]

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        # Yaw from quaternion
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    def scan_callback(self, msg):
        self.front_distance = self._range_in_window(msg, 0.0)
        self.left_distance = self._range_in_window(msg, math.pi / 2.0)
        self.right_distance = self._range_in_window(msg, -math.pi / 2.0)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _range_in_window(self, scan, center_angle, half_width=0.26):
        """Smallest valid range within +/- half_width rad of center_angle.

        Works for any scan configuration because it derives each beam's
        angle from angle_min / angle_increment rather than assuming an
        index layout.
        """
        n = len(scan.ranges)
        if n == 0:
            return float('inf')

        best = float('inf')
        for i in range(n):
            angle = scan.angle_min + i * scan.angle_increment
            diff = math.atan2(
                math.sin(angle - center_angle),
                math.cos(angle - center_angle)
            )
            if abs(diff) <= half_width:
                r = scan.ranges[i]
                if math.isfinite(r) and r >= scan.range_min and r < best:
                    best = r
        return best

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    # ------------------------------------------------------------------ #
    # Control loop
    # ------------------------------------------------------------------ #
    def control_loop(self):
        # Wait until target and odometry are available.
        if self.target_x is None or self.robot_x is None or self.robot_yaw is None:
            return

        dx = self.target_x - self.robot_x
        dy = self.target_y - self.robot_y
        distance = math.hypot(dx, dy)

        target_angle = math.atan2(dy, dx)
        heading_error = math.atan2(
            math.sin(target_angle - self.robot_yaw),
            math.cos(target_angle - self.robot_yaw)
        )

        cmd = Twist()

        if self.front_distance < self.obstacle_threshold:
            # Obstacle ahead: stop forward motion, turn to the open side.
            cmd.linear.x = 0.0
            if self.left_distance >= self.right_distance:
                cmd.angular.z = self.max_angular
            else:
                cmd.angular.z = -self.max_angular

        elif distance <= self.stop_distance:
            # Close enough to the target: hold position.
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        else:
            # Head toward the target.
            cmd.angular.z = self._clamp(
                1.5 * heading_error,
                -self.max_angular,
                self.max_angular
            )
            # Only drive forward once roughly facing the target.
            if abs(heading_error) < 0.5:
                cmd.linear.x = self._clamp(
                    0.4 * distance,
                    0.0,
                    self.max_linear
                )
            else:
                cmd.linear.x = 0.0

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = EscortController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
