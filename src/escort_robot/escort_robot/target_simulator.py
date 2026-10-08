import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class TargetSimulator(Node):
    """Publishes a fixed target position on /target_position.

    Later this node can be swapped for a real person tracker
    (camera + OpenCV) that publishes to the same topic, and the
    escort_controller does not have to change.
    """

    def __init__(self):
        super().__init__('target_simulator')

        self.publisher = self.create_publisher(
            Float32MultiArray,
            '/target_position',
            10
        )

        self.target_x = 5.0
        self.target_y = 0.0

        self.timer = self.create_timer(
            0.2,
            self.publish_target
        )

    def publish_target(self):
        msg = Float32MultiArray()
        msg.data = [
            self.target_x,
            self.target_y
        ]
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TargetSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
