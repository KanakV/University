# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 12:07:01 2025

@author: PC-Kanak
"""
import numpy as np


def forward_kin(joint_angles):
    
    T_x = (0.13333 + 0.0996 * np.cos(joint_angles[4])) * np.sin(joint_angles[0]) + np.cos(joint_angles[0]) * (
        -0.425 * np.cos(joint_angles[1]) - 0.3922 * np.cos(joint_angles[1] + joint_angles[2])
        + 0.0997 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3])
        + 0.0498 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3] - joint_angles[4])
        - 0.0498 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3] + joint_angles[4])
    )

    T_y = np.cos(joint_angles[0]) * (-0.13333 - 0.0996 * np.cos(joint_angles[4])) + np.sin(joint_angles[0]) * (
        -0.425 * np.cos(joint_angles[1]) - 0.3922 * np.cos(joint_angles[1] + joint_angles[2])
        + 0.0997 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3])
        + 0.0498 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3] - joint_angles[4])
        - 0.0498 * np.sin(joint_angles[1] + joint_angles[2] + joint_angles[3] + joint_angles[4])
    )

    T_z = (
        0.1625
        - 0.0997 * np.cos(joint_angles[1] + joint_angles[2] + joint_angles[3])
        - 0.0498 * np.cos(joint_angles[1] + joint_angles[2] + joint_angles[3] - joint_angles[4])
        + 0.0498 * np.cos(joint_angles[1] + joint_angles[2] + joint_angles[3] + joint_angles[4])
        - 0.425 * np.sin(joint_angles[1])
        - 0.3922 * np.sin(joint_angles[1] + joint_angles[2])
    )
    
    pos = [T_x, T_y, T_z]
    return pos