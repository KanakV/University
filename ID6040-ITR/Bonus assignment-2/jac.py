# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 22:00:41 2025

@author: PC-Kanak
"""
import numpy as np
import sympy as sp


theta1, theta2, theta3, theta4, theta5 = sp.symbols('theta1 theta2 theta3 theta4 theta5')

T_x = (0.13333 + 0.0996 * sp.cos(theta5)) * sp.sin(theta1) + sp.cos(theta1) * (
    -0.425 * sp.cos(theta2) - 0.3922 * sp.cos(theta2 + theta3)
    + 0.0997 * sp.sin(theta2 + theta3 + theta4)
    + 0.0498 * sp.sin(theta2 + theta3 + theta4 - theta5)
    - 0.0498 * sp.sin(theta2 + theta3 + theta4 + theta5)
)

T_y = sp.cos(theta1) * (-0.13333 - 0.0996 * sp.cos(theta5)) + sp.sin(theta1) * (
    -0.425 * sp.cos(theta2) - 0.3922 * sp.cos(theta2 + theta3)
    + 0.0997 * sp.sin(theta2 + theta3 + theta4)
    + 0.0498 * sp.sin(theta2 + theta3 + theta4 - theta5)
    - 0.0498 * sp.sin(theta2 + theta3 + theta4 + theta5)
)

T_z = (
    0.1625
    - 0.0997 * sp.cos(theta2 + theta3 + theta4)
    - 0.0498 * sp.cos(theta2 + theta3 + theta4 - theta5)
    + 0.0498 * sp.cos(theta2 + theta3 + theta4 + theta5)
    - 0.425 * sp.sin(theta2)
    - 0.3922 * sp.sin(theta2 + theta3)
)

F = sp.Matrix([T_x, T_y, T_z])
X = sp.Matrix([theta1, theta2, theta3, theta4, theta5])

J_sym = F.jacobian(X)

print(J_sym.shape)
