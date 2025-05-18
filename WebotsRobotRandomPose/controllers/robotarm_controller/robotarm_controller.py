"""robotarm_controller controller."""
from controller import Robot, Supervisor
import pyikfast_irb140 as ik
import numpy as np
import pose_estimation
import random

robot = Supervisor()

timestep = 64

home_position = [0.5225, 0.712, 0]
home_rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
demo_positions = [[0.5225, 0.712, 0],
                  [0.5225, 0.8, 0],
                  [0.5, 0.8, 0],
                  [0.55, 0.8, 0],
                  [0.5225, 0.8, 0.1],
                  [0.5, 0.8, 0.1],
                  [0.55, 0.8, -0.1],
                  [0.5225, 0.8, -0.1],
                  [0.55, 0.3, -0.45], 
                  [0.2, 0.5, -0.4]]
demo_rotations = [[0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                  [0,  0, -1,
                   -0.5555702,  0.8314696, -0,
                   0.8314696,  0.5555702,  0],
                  [0.5,  0.5, -0.7071068,
                   -0.7071068,  0.7071068,  0,
                   0.5,  0.5,  0.7071068]
                  ]

targets = {}

# controller variables
motors = []
sensors = []
motors_pos = []
min_positions = []
max_positions = []

camera = robot.getDevice("camera")
camera.enable(timestep)
distance_sensor = robot.getDevice("distance sensor")
distance_sensor.enable(timestep)


motors.append(robot.getDevice("rm_base"))
motors[0].setVelocity(1)
min_positions.append(robot.getDevice("rm_base").getMinPosition())
max_positions.append(robot.getDevice("rm_base").getMaxPosition())
sensors.append(motors[0].getPositionSensor())

for j in range(5):
    motor = robot.getDevice("rm_axis" + str(j + 1))

    motors.append(motor)
    sensors.append(motor.getPositionSensor())

    min_positions.append(motor.getMinPosition())
    max_positions.append(motor.getMaxPosition())

    motor.setVelocity(1)

for sensor in sensors:
    sensor.enable(timestep)
    motors_pos.append(sensor.getValue())


def waiting(ik_results):
    current_pos = [0, 0, 0, 0, 0, 0]
    while not np.allclose(ik_results, current_pos, atol=0.001):
        robot.step(timestep)
        for i in range(len(sensors)):
            current_pos[i] = sensors[i].getValue()


def get_target_relative_pos(target_pos, target_rot):
    robot_base_pos = np.array([0, 0, 0])
    robot_base_rot = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    target_world_pos = np.array(target_pos)
    target_world_rot = np.array(target_rot).reshape(3, 3)

    target_relative_pos = list(np.subtract(np.dot(robot_base_rot, target_world_pos), robot_base_pos))
    target_relative_rot = np.dot(robot_base_rot, target_world_rot)

    target_relative_rot = list(np.reshape(target_relative_rot, 9))

    return target_relative_pos, target_relative_rot


def within_bounds(results):
    bounds_min = np.array(min_positions[:6])
    bounds_max = np.array(max_positions[:6])
    mask = np.array(np.zeros(len(results)), dtype=bool)

    for i in range(len(results)):
        mask[i] = (all(results[i] > bounds_min) and all(results[i] < bounds_max))

    return mask


def calc_ik(target_pos, target_rot):
    ik_results = np.array(ik.inverse(target_pos, target_rot))
    joint2_offset = 0
    n_joints = 6
    old_ik_results = np.zeros(n_joints)

    try:
        # [-pi, pi] instead of [0, 2*pi]
        ik_results = np.where(ik_results > np.pi, ik_results - 2 * np.pi, ik_results)

        # check motor limits
        mask = within_bounds(ik_results)
        ik_results = ik_results[mask, :]

        # third joint as high as possible
        height_joint3 = np.cos(ik_results[:, 1] - joint2_offset) * 5

        # least rotation in the first joint
        joint1_delta = np.multiply(np.abs(np.subtract(ik_results[:, 0], old_ik_results[0])), 2)

        # least rotation in joint4,5 (wrist flipping aroud)
        joint45_delta = np.abs(np.subtract(ik_results[:, 3:5], old_ik_results[3:5])).sum(axis=1)

        ik_result_var = height_joint3 - (joint1_delta + joint45_delta)

        index = np.argmax(ik_result_var)

        return ik_results[index]

    except:
        print('No solution found for point {}'.format(target_pos))
        return []


def save_ik(name, pos, rot):
    target_pos, target_rot = get_target_relative_pos(pos, rot)
    targets[name] = calc_ik(target_pos, target_rot)


def go_to(name):
    for i in range(len(targets[name])):
        motors[i].setPosition(targets[name][i])
    waiting(targets[name])
    
save_ik("home", home_position, home_rotation)

for i in range(len(demo_positions)):
    save_ik(str(i), demo_positions[i], demo_rotations[i])

go_to("home")

for i in range(len(demo_positions)):
    go_to(str(i))
    camera.saveImage(chr(i+65) + '.png', 100)



#pose_estimation.findpose(False)
mtx, dist, R_cam2gripper, t_cam2gripper = pose_estimation.findpose(True, demo_positions, demo_rotations)
print(t_cam2gripper)
go_to('0')
camera.saveImage("~0.png", 100)
R_base2object, t_base2object = pose_estimation.worldposecalc("~0.png", True, mtx, dist, demo_rotations[0], demo_positions[0], R_cam2gripper, t_cam2gripper)
save_ik("object", t_base2object, R_base2object)
go_to("object")

save_ik("objpic2", [0.48, 0.7, 0.20], [0.0, 0.0, 1.0, -0.3826834, 0.9238795, 0.0, -0.9238795, -0.3826834, 0.0])
go_to("objpic2")
camera.saveImage("~1.png", 100)
R_base2object, t_base2object = pose_estimation.worldposecalc("~1.png", True, mtx, dist, [0.0, 0.0, 1.0, -0.3826834, 0.9238795, 0.0, -0.9238795, -0.3826834, 0.0], [0.48, 0.7, 0.20], R_cam2gripper, t_cam2gripper)
save_ik("object", t_base2object, R_base2object)
go_to("object")


checkerboard = robot.getFromDef("checkerboard")
translation_field = checkerboard.getField("translation")

save_ik("random", [0.5225, 0.81, 0], demo_rotations[0])


while True:
    translation_field.setSFVec3f([random.uniform(0.465, 0.58), random.uniform(-0.15, 0.1), 0.01])   
    actual_t = translation_field.getSFVec3f()
    
    go_to("random")
    camera.saveImage("~random.png", 100)
    R_base2object, t_base2object = pose_estimation.worldposecalc("~random.png", True, mtx, dist, demo_rotations[0], [0.5225, 0.81, 0], R_cam2gripper, t_cam2gripper)
    distance = np.linalg.norm(np.array(actual_t) - np.array(t_base2object))
    print(t_base2object)
    print(actual_t)
    print("Hiba: ", distance, "")
    save_ik("object", t_base2object, R_base2object)
    go_to("object")
    