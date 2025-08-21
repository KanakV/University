import math
import numpy as np
import forward_kin as fk

def is_in_vicinity(point1, point2, threshold):
    distance = np.linalg.norm(np.array(point1) - np.array(point2))  # Euclidean distance
    return distance <= threshold

def inv_kin(desired_end_effector_position):
    #Compute the joint angles [in radians] for desired end effector position [in meters] 

    desired_pos = np.array(desired_end_effector_position)
    
    steps = 1000
    threshold = 1e-3
    ### Fill this part ###
    current_theta = np.array([0, 0, 0, 0, 0])
    current_pos = np.array(jacobian(*current_theta) @ current_theta)
    ddistance = (desired_pos - current_pos) / steps

    while not is_in_vicinity(desired_pos, current_pos, threshold):    
        dtheta = np.linalg.pinv(jacobian(*current_theta)) @ ddistance
        current_theta = current_theta + dtheta
#        current_pos = current_pos + np.array(jacobian(*current_theta) @ dthera)
        current_pos = fk.forward_kin(current_theta)
        ddistance = (desired_pos - current_pos) / steps

    
    joint_angles = current_theta
    return joint_angles


def jacobian(theta1, theta2, theta3, theta4, theta5):
    jac = [
        [(0.0996*np.cos(theta5) + 0.13333)*np.cos(theta1) - (0.0997*np.sin(theta2 + theta3 + theta4) + 0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5) - 0.425*np.cos(theta2) - 0.3922*np.cos(theta2 + theta3))*np.sin(theta1), 
         (0.425*np.sin(theta2) + 0.3922*np.sin(theta2 + theta3) + 0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.cos(theta1), 
         (0.3922*np.sin(theta2 + theta3) + 0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.cos(theta1), 
         (0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.cos(theta1), 
         (-0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.cos(theta1) - 0.0996*np.sin(theta1)*np.sin(theta5)
         ], 
        [-(-0.0996*np.cos(theta5) - 0.13333)*np.sin(theta1) + (0.0997*np.sin(theta2 + theta3 + theta4) + 0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5) - 0.425*np.cos(theta2) - 0.3922*np.cos(theta2 + theta3))*np.cos(theta1), 
         (0.425*np.sin(theta2) + 0.3922*np.sin(theta2 + theta3) + 0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.sin(theta1), 
         (0.3922*np.sin(theta2 + theta3) + 0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.sin(theta1), 
         (0.0997*np.cos(theta2 + theta3 + theta4) + 0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.sin(theta1), 
         (-0.0498*np.cos(theta2 + theta3 + theta4 - theta5) - 0.0498*np.cos(theta2 + theta3 + theta4 + theta5))*np.sin(theta1) + 0.0996*np.sin(theta5)*np.cos(theta1)
         ], 
        [0, 
         0.0997*np.sin(theta2 + theta3 + theta4) + 0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5) - 0.425*np.cos(theta2) - 0.3922*np.cos(theta2 + theta3),
         0.0997*np.sin(theta2 + theta3 + theta4) + 0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5) - 0.3922*np.cos(theta2 + theta3),
         0.0997*np.sin(theta2 + theta3 + theta4) + 0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5),
         -0.0498*np.sin(theta2 + theta3 + theta4 - theta5) - 0.0498*np.sin(theta2 + theta3 + theta4 + theta5)
         ]]
    return jac