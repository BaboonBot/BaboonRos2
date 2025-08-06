import rclpy                                     # ROS2 Python interface library
from rclpy.node import Node                      # ROS2 Node class
import time

"""
Create a HelloWorld node and output the "hello world" log during initialization
"""
class HelloWorldNode(Node):
    def __init__(self, name):
        super().__init__(name)                     # ROS2 node parent class initialization
        while rclpy.ok():                          # Whether the ROS2 system is running normally
            self.get_logger().info("Hello World")  # ROS2 log output
            time.sleep(0.5)                        # sleep control loop time

def main(args=None):                               # ROS2 node main entrance main function
    rclpy.init(args=args)                          # ROS2 Python interface initialization
    node = HelloWorldNode("helloworld")            # Create a ROS2 node object and initialize it
    rclpy.spin(node)                               # Loop waiting for ROS2 to exit
    node.destroy_node()                            # Destroy node object
    rclpy.shutdown()                               # Close the ROS2 Python interface