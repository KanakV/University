# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 12:05:19 2025

@author: PC-Kanak
"""

import inv_kin as ik
import forward_kin as fk
import random as rand
import numpy as np

def main():
    joint_angles = []
    for _ in range(5):
        joint_angles.append(rand.random() * 2 * np.pi)
    # Joint Angles in Radians
    
    desired = fk.forward_kin(joint_angles)
    
    print("Desired End Effector Position: ", desired, "\n\n")
    

    actual_joint_angles = ik.inv_kin(desired)
    actual = fk.forward_kin(actual_joint_angles)
    print("Actual End Effector Position: ", actual, "\n\n")
    
#    print("Joint Angles: ", joint_angles, "\n\n")
#    print("Actual Joint Angles: ", actual_joint_angles, "\n\n")

    


if __name__ == "__main__":
    main()



