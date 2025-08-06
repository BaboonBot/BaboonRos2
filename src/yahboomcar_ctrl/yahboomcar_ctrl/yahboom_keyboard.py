#!/usr/bin/env python
# encoding: utf-8
#import public lib
from geometry_msgs.msg import Twist
import sys, select, termios, tty

#import ros lib
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

msg = """
Control Your SLAM-Bot!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
t/T : x and y speed switch
s/S : stop keyboard control
V/B : subtract/add 1 to angle node
space key, k : force stop
anything else : stop smoothly

CTRL-C to quit
"""

moveBindings = {
    'i': (1, 0),
    'o': (1, -1),
    'j': (0, 1),
    'l': (0, -1),
    'u': (1, 1),
    ',': (-1, 0),
    '.': (-1, 1),
    'm': (-1, -1),
    'I': (1, 0),
    'O': (1, -1),
    'J': (0, 1),
    'L': (0, -1),
    'U': (1, 1),
    'M': (-1, -1),
}

speedBindings = {
    'Q': (1.1, 1.1),
    'Z': (.9, .9),
    'W': (1.1, 1),
    'X': (.9, 1),
    'E': (1, 1.1),
    'C': (1, .9),
    'q': (1.1, 1.1),
    'z': (.9, .9),
    'w': (1.1, 1),
    'x': (.9, 1),
    'e': (1, 1.1),
    'c': (1, .9),
}



class Yahboom_Keybord(Node):
	def __init__(self,name):
		super().__init__(name)
		self.pub = self.create_publisher(Twist,'cmd_vel',1)
		self.pub_angle = self.create_publisher(Twist,'angle_vel',1)
		self.declare_parameter("linear_speed_limit",1.0)
		self.declare_parameter("angular_speed_limit",5.0)
		self.linenar_speed_limit = self.get_parameter("linear_speed_limit").get_parameter_value().double_value
		self.angular_speed_limit = self.get_parameter("angular_speed_limit").get_parameter_value().double_value
		self.settings = termios.tcgetattr(sys.stdin)
	def getKey(self):
		tty.setraw(sys.stdin.fileno())
		rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
		if rlist: key = sys.stdin.read(1)
		else: key = ''
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
		return key
	def vels(self, speed, turn):
		return "currently:\tspeed %s\tturn %s " % (speed,turn)		
	
def main():
	rclpy.init()
	yahboom_keyboard = Yahboom_Keybord("yahboom_keyboard_ctrl")
	xspeed_switch = True
	(speed, turn) = (0.2, 1.0)
	(x, th) = (0, 0)
	current_angle = 0.0  # Track current angle value
	speed = 10.0
	status = 0
	stop = False
	count = 0
	twist = Twist()
	angle_twist = Twist()
	try:
		print(msg)
		print(yahboom_keyboard.vels(speed, turn))
		while (1):
			key = yahboom_keyboard.getKey()
			if key=="t" or key == "T": xspeed_switch = not xspeed_switch
			elif key == "s" or key == "S":
				print ("stop keyboard control: {}".format(not stop))
				stop = not stop
			elif key.lower() == 'v':
				current_angle -= speed
				if current_angle < 0:  # Ensure angle stays within bounds
					current_angle = 0.0
				print(f"Angle decreased to: {current_angle}")
				count = 0
			elif key.lower() == 'b':
				current_angle += speed
				if current_angle > 180.0:  # Ensure angle stays within bounds
					current_angle = 180.0
				print(f"Angle increased to: {current_angle}")
				count = 0
			if key in moveBindings.keys():
				x = moveBindings[key][0]
				th = moveBindings[key][1]
				count = 0
			elif key in speedBindings.keys():
				speed = speed * speedBindings[key][0]
				turn = turn * speedBindings[key][1]
				count = 0
				if speed > yahboom_keyboard.linenar_speed_limit: 
					speed = yahboom_keyboard.linenar_speed_limit
					print("Linear speed limit reached!")
				if turn > yahboom_keyboard.angular_speed_limit: 
					turn = yahboom_keyboard.angular_speed_limit
					print("Angular speed limit reached!")
				print(yahboom_keyboard.vels(speed, turn))
				if (status == 14): print(msg)
				status = (status + 1) % 15
			elif key == ' ': (x, th) = (0, 0)
			else:
				count = count + 1
				if count > 4: (x, th) = (0, 0)
				if (key == '\x03'): break
			if xspeed_switch: twist.linear.x = speed * x
			else: twist.linear.y = speed * x
			twist.angular.z = turn * th
			
			# Set the angle twist message
			angle_twist.angular.z = current_angle
			
			if not stop: 
				yahboom_keyboard.pub.publish(twist)
				yahboom_keyboard.pub_angle.publish(angle_twist)
				if current_angle != 0.0:  # Only print when angle is non-zero
					print(f"Publishing angle: {current_angle}")
			else:
				# When stopped, still publish angle but stop movement
				yahboom_keyboard.pub.publish(Twist())
				yahboom_keyboard.pub_angle.publish(angle_twist)
				if current_angle != 0.0:  # Only print when angle is non-zero
					print(f"Publishing angle (stopped): {current_angle}")
	except Exception as e: print(e)
	finally: yahboom_keyboard.pub.publish(Twist())
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, yahboom_keyboard.settings)
	yahboom_keyboard.destroy_node()
	rclpy.shutdown()
