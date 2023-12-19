import numpy as np
from scipy.spatial.transform import Rotation as R

demo_positions = [[0.465, 0.0005, 0.5768],
           [0.465, 0.0005, 0.6641],
           [0.465, 0.0005, 0.5144],
           [0.4651, -0.089, 0.5765],
           [0.4651, -0.0578, 0.5765],
           [0.4651, 0.0477, 0.5765],
           [0.4651, 0.0633, 0.5765],
           [0.4814, 0.0003, 0.5765],
           [0.4376, 0.0003, 0.5765],
           [0.4376, 0.0628, 0.5765],
           [0.4466, -0.0827, 0.5765],
           [0.4729, -0.0827, 0.5765],
           [0.4729, 0.059, 0.5765],
            [0.4856, -0.0853, 0.7126]]

demo_rotations = [[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-90,0,89.9],
[-45,-0.1,90.2]]

rot_matrices = []

for angles in demo_rotations:
    # Convert degrees to radians
    angles_rad = np.radians(angles)

    # Create a Rotation object from Euler angles
    rotation = R.from_euler('zyx', angles_rad, degrees=True)

    # Get the 3x3 rotation matrix
    rotation_matrix = rotation.as_matrix().flatten().tolist()

    rot_matrices.append(rotation_matrix)

demo_rotations = rot_matrices

import pose_estimation

mtx, dist, R_cam2gripper, t_cam2gripper = pose_estimation.findpose(True, demo_positions, demo_rotations)
print(t_cam2gripper)
