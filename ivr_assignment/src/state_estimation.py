#!/usr/bin/env python3

import roslib
import sys
import rospy
import cv2
import numpy as np
from std_msgs.msg import Float64MultiArray, Int16MultiArray

class joint_state:
    def __init__(self):
        # initialize the node named joint_processing
        rospy.init_node('joint_processing', anonymous=True)

        # initialize subscribers to receive the coordinates of the joints
        self.robot_x_z = rospy.Subscriber("/robot/x_z", Int16MultiArray, self.callback1)
        self.robot_y_z = rospy.Subscriber("/robot/y_z", Int16MultiArray, self.callback2)
        # initialize a publisher for joint angles
        self.joints_pub = rospy.Publisher("/joints_ang", Float64MultiArray, queue_size=10)
        # initialize a publisher for target object position
        self.target_pub = rospy.Publisher("/target_pos", Int16MultiArray, queue_size=10)
        #[red_x,red_z,green_x,green_z,blue_x,blue_z,target_x,target_z]
        self.x_z = None
        # [red_y,red_z,green_y,green_z,blue_y,blue_z,target_y,target_z]
        self.y_z = None

    def detect_joint_angles(self,red,green,blue):
        new_z_1 = np.sqrt((green[0]-blue[0])**2+(green[2]-blue[2])**2)
        joint_2 = np.arctan2(np.abs(green[1]-blue[1]),np.abs(green[2]-blue[2]))
        if(green[1]>blue[1]):
            joint_2 = -joint_2
        new_z_2 = np.sqrt((green[1]-blue[1])**2+(green[2]-blue[2])**2)
        joint_3 = np.arctan2(np.abs(green[0]-blue[0]),new_z_2)
        if (green[0]<blue[0]):
            joint_3 = -joint_3
        green_to_blue = blue - green
        green_to_red = red - green
        joint_4 = np.pi - np.arccos(np.dot(green_to_blue, green_to_red) /
                                    (np.linalg.norm(green_to_blue) * np.linalg.norm(green_to_red)))
        if(red[0]<green[0]):
            joint_4 = -joint_4
        return np.array([joint_2,joint_3,joint_4])

    # Recieve data, process it
    def callback1(self,data):
        self.x_z = data.data
        self.joint_estimate()
    # Recieve data, process it
    def callback2(self, data):
        self.y_z = data.data
        self.joint_estimate()


    def joint_estimate(self):
        if(self.x_z != None and self.y_z != None):
            # xz [red_x,red_z,green_x,green_z,blue_x,blue_z,target_x,target_z]
            # yz [red_y,red_z,green_y,green_z,blue_y,blue_z,target_y,target_z]
            self.red_x = self.x_z[0]
            self.red_y = self.y_z[0]
            self.red_z_1 = self.x_z[1]
            self.red_z_2 = self.y_z[1]
            self.green_x = self.x_z[2]
            self.green_y = self.y_z[2]
            self.green_z_1 = self.x_z[3]
            self.green_z_2 = self.y_z[3]
            self.blue_x = self.x_z[4]
            self.blue_y = self.y_z[4]
            self.blue_z_1 = self.x_z[5]
            self.blue_z_2 = self.y_z[5]
            self.target_x = self.x_z[6]
            self.target_y = self.y_z[6]
            self.target_z_1 = self.x_z[7]
            self.target_z_2 = self.y_z[7]
            if(self.red_z_2 == 0):self.red_z = self.red_z_1
            else: self.red_z = self.red_z_2
            if (self.green_z_2 == 0):self.green_z = self.green_z_1
            else:self.green_z = self.green_z_2
            if (self.blue_z_2 == 0):self.blue_z = self.blue_z_1
            else:self.blue_z = self.blue_z_2
            if (self.target_z_2 == 0): self.target_z =self.target_z_1
            else:self.target_z = self.target_z_2
            self.red = np.array([self.red_x-392,self.red_y-392,self.red_z-529])
            self.green = np.array([self.green_x-392,self.green_y-392,self.green_z-529])
            self.blue = np.array([self.blue_x-392,self.blue_y-392,self.blue_z-529])
            self.target = np.array([392-self.target_x,392-self.target_y,529-self.target_z])
            #self.yellow = np.array([0,0,0])
            self.joint_angles = Float64MultiArray()
            self.joint_angles.data = self.detect_joint_angles(self.red,self.green,self.blue)
            self.target_pos = Int16MultiArray()
            self.target_pos.data = self.target
            # Publish the joint angles
            self.joints_pub.publish(self.joint_angles)
            self.target_pub.publish(self.target_pos)


# call the class
def main(args):
  ic = joint_state()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

# run the code if the node is called
if __name__ == '__main__':
    main(sys.argv)