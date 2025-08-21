# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:01:49 2023

@author: Bijo Sebastian
"""

import math
import numpy as np
import robot_params as rp

def inv_kin_fn(goal_position):
    #Compute joint angles [in degrees] to reach desired position [in meters] 
    x_desired = goal_position[0]
    y_desired = goal_position[1]
    
    ct2 = (x_desired**2 + y_desired**2 - rp.link_1_length**2 - rp.link_2_length**2)/ (2 * rp.link_1_length * rp.link_2_length)
    st2 = math.sqrt(1 - ct2**2)
    
    theta_2 = math.atan2(st2,ct2)
    
    theta_1 = math.atan2(y_desired, x_desired) - math.atan2(rp.link_2_length * st2, 
                                                            rp.link_1_length + rp.link_2_length * ct2)

    theta_1 *= (180 / math.pi)
    theta_2 *= (180 / math.pi)
    print("Desired joint angles",[theta_1, theta_2])
    return [theta_1, theta_2]