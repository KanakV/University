import math
import robot_params

def fw_kin(joint_angles):
    #Compute end effector position [in meters] for the given pair of joint angles [in degrees] 
    
    
    ### Fill this part ###
    #Hint: see file robot_params for link lengths
    joint_angles[0] *= math.pi / 180
    joint_angles[1] *= math.pi / 180
    
    x_end_effector = robot_params.link_1_length * math.cos(joint_angles[0]) + robot_params.link_2_length * math.cos(joint_angles[0] + joint_angles[1])
    y_end_effector = robot_params.link_1_length * math.sin(joint_angles[0]) + robot_params.link_2_length * math.sin(joint_angles[0] + joint_angles[1])
    
    end_effector_position_analytic = [x_end_effector, y_end_effector]
    
    print("End effector position (analytic)", end_effector_position_analytic)
    return end_effector_position_analytic