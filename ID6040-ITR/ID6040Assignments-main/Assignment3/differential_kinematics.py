# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 09:51:21 2023

@author: Bijo Sebastian
"""
import numpy as np
import robot_params as rp

def get_desired_joint_rate(joint_angles):
    
    theta1 = joint_angles[0]
    theta2 = joint_angles[1]
    
    #Compute 2x2 jacobian matrix for given joint angles [in radians] 
    j11 = -rp.link_1_length * np.sin(theta1) - rp.link_2_length * np.sin(theta1 + theta2)
    j12 = -rp.link_2_length * np.sin(theta1 + theta2)
    j21 =  rp.link_1_length * np.cos(theta1) + rp.link_2_length * np.cos(theta1 + theta2)
    j22 =  rp.link_2_length * np.cos(theta1 + theta2)
    jacobian  = np.array([[j11, j12], [j21, j22]])
    inv_jacobian = np.linalg.inv(jacobian)
    
    #Compute desired joint angle rate by inverting jacobian and multiplying with desired end effector velocity
    desired_end_effector_velocity = np.array([[0.01], [0.0]])
    desired_joint_angle_rates =  inv_jacobian @ desired_end_effector_velocity
    
    return [desired_joint_angle_rates[0], desired_joint_angle_rates[1]]