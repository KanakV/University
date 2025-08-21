# ID6040 Assignment 2 
Implement inverse kinematics for a two link manipulator in Coppleiasim(V-REP)

## Setup:
OS: Windows 10/11; Ubuntu 20.04

Python: 3.6.x
Coppeliasim: V4.3.0

## Instructions:

  1. Download the setup provided in this repository. If you are familiar with how to use git on windows do that, if not click on the green button that says code and click on download zip. Once the download is complete, double click to extract the contents and place them in a location of your choice, the downloads folder itself works fine.

  2. For the 2 DOF planar manipulator, compute the pair of joint angles(in degrees) for a given end effector position. See the file robot_params.py for link length.

  3. Complete the inverse kinematics function in the file **inv_kin.py**. Do not make any changes to the other code files provided to you.
  
  4. Once you have completed the inverse kinematic implementation, launch Coppeliasim. Click on File->Open Scene, navigate to the downloaded setup, and select the file **2R_manipulator.ttt**. Run the simulation by clicking on the light blue play button.

  5. Launch Spyder. Click on File -> Open and navigate to the downloaded setup. Select the file Assignment_2.py. Run the file by clicking on the green play button.

  6. Always ensure that the simulation is running before you launch the code, otherwise you will get an error that says "Failed connecting to the remote API server. Program ended".

  7. If your implementation of the inverse kinematics calculation was correct, you will get a printout on your terminal that says Exercise 2 result: Success

