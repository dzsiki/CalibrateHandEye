"""irb140_controller controller."""
import pickle
import random

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Supervisor
from visual_kinematics.RobotSerial import RobotSerial, Frame
import numpy as np


# Set the precision for printing numpy arrays
np.set_printoptions(suppress=True, precision=4)


# Function to determine joint values from coordinates:
def do_ik(robot_inst, pose_values, ori_mode='euler'):
    """
    Compute the inverse kinematics of the robot

    :param robot_inst: RobotSerial instance
    :param pose_values: Coordinates and orientation of the end effector, ori: axis-angle orientation, coord: x, y, z
    :param ori_mode: The orientation mode, axis-angle or euler
    :return: The joint values
    """
    ori = pose_values[3:]
    coord = np.reshape(pose_values[:3], (3, 1))  # must be a column vector
    target_frame_rs = None
    if ori_mode == 'axis_angle':
        target_frame_rs = Frame.from_r_3(ori, coord)  # axis-angle - from_r_3
    elif ori_mode == 'euler':
        target_frame_rs = Frame.from_euler_3(ori, coord)  # ZYX - from_euler_3
    try:
        joint_values = robot_inst.inverse(target_frame_rs)
    except Exception as e:
        print(e)
        joint_values = [0, 0, 0, 0, 0, 0]
    return joint_values


# IRB-140 robot parameters
d1, a1, alpha1, theta1 = 0.352, 0.07, -np.pi / 2, 0.
d2, a2, alpha2, theta2 = 0., -0.360, 0., np.pi / 2
d3, a3, alpha3, theta3 = 0., 0., np.pi / 2, 0.
d4, a4, alpha4, theta4 = 0.380, 0., -np.pi / 2, 0.
d5, a5, alpha5, theta5 = 0., 0., np.pi / 2, 0.
d6, a6, alpha6, theta6 = 0.065, 0., 0., 0.

# IRB-140 robot DH parameter matrix
dh_irb_140 = np.array([[d1, a1, alpha1, theta1],
                       [d2, a2, alpha2, theta2],
                       [d3, a3, alpha3, theta3],
                       [d4, a4, alpha4, theta4],
                       [d5, a5, alpha5, theta5],
                       [d6, a6, alpha6, theta6]])

# Create the RobotSerial instance
robot_serial = RobotSerial(dh_irb_140)


# --------------- Webots ---------------------

# Move motors based on the joint values
def move_motors(robot_motors, joint_values):
    for idx, val in enumerate(joint_values):
        robot_motors[idx].setPosition(val)


def get_sensors_values(robot_sensors):
    current_pos = []
    for sensor_obj in robot_sensors:
        current_pos.append(sensor_obj.getValue())
    return np.array(current_pos)


# Wait until the robot reaches the target position
def is_position_reached(robot_sensors, joint_values, verbose=False):
    """
    If joint values are close to the sensor values then robot reached the position.

    :param robot_sensors: Robot sensors
    :param joint_values: Joint values
    :param verbose: Verbose mode
    :returns Bool, True is reached
    """
    sensor_values = get_sensors_values(robot_sensors)
    is_reached = np.allclose(sensor_values, joint_values, atol=0.01)
    while not is_reached:
        # Warning! Can cause a deadlock if the position is never reached
        robot.step(timestep)  # step the simulation to move closer to the target
        sensor_values = get_sensors_values(robot_sensors)
        is_reached = np.allclose(sensor_values, joint_values, atol=0.01)
        if verbose:
            print(sensor_values, joint_values, is_reached)
    return True


# create the Robot instance.
robot = Supervisor()
# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
motors = []
sensors = []
min_positions = []
max_positions = []

# Get the camera and enable it
camera = robot.getDevice("camera")
camera.enable(timestep)


for j in range(len(dh_irb_140)):
    motor = robot.getDevice("joint_" + str(j + 1))
    motor.setVelocity(np.pi / 4)  # rad/s
    motors.append(motor)
    sensors.append(motor.getPositionSensor())

    min_positions.append(motor.getMinPosition())
    max_positions.append(motor.getMaxPosition())

for sensor in sensors:
    sensor.enable(timestep)

# Dedicated coordinates
home = np.array([0.45, 0.0, 0.647, 0, np.pi, 0])
# Test coordinates
#coords_list = [home, np.array([0.45, 0.174, 0.647, 0, np.pi, 0]), home]
#coords_list = [np.array([0.551377372112,0.0,0.647000003554,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.5516697665200001,0.157633351376,0.646999996348,-2.943846849338835,0.0,3.141592653589793]),np.array([0.5513773618410001,-0.168242049442,0.7603029467310001,-3.141592653589793,0.0,3.141592653589793]),np.array([0.496852655447,0.06202713065,0.587887151403,-3.141592653589793,0.0,3.141592653589793]),np.array([0.557560360984,0.052411594086999996,0.5878871592220001,-2.4457298808196537,0.0,-3.141592653589793]),np.array([0.557560364232,0.052411594392,0.726092859148,-2.4457298808196537,0.0,-3.141592653589793]),np.array([0.5767592708339999,0.0026559649259999996,0.73760776979,-1.7130406608324344,0.0,3.141592653589793]),np.array([0.449999997695,-0.241094115961,0.7061770503389999,3.141592653589793,0.0,2.5902431428847845]),np.array([0.270421878488,0.0,0.622506419081,-3.141592653589793,0.6709045644666202,-3.141592653589793]),np.array([0.5106230222170001,0.0,0.647000009727,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.38785909461699997,0.0,0.6470000065770001,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.450000008384,0.036398472429,0.647000007402,3.141592653589793,0.0,-3.141592653589793]),np.array([0.450000008354,-0.052389891667999997,0.6470000073569999,-3.141592653589793,0.0,3.141592653589793]),np.array([0.454393408506,-0.010606603692,0.647000007373,-2.356194490192345,0.0,-3.141592653589793]),np.array([0.454393406435,-0.010606603644,0.7596036791940001,-2.356194490192345,0.0,-3.141592653589793]),np.array([0.450331271764,-0.003135258428,0.7240132144520001,-2.9311059457992767,0.0,3.141592653589793]),np.array([0.450000012901,0.0,0.588588113076,3.141592653589793,0.0,-3.141592653589793]),np.array([0.18598799590999998,0.0,0.6378379588,-3.141592653589793,0.3440043955680824,-3.141592653589793]),np.array([0.450000006623,-0.147331700946,0.6451367517050001,3.141592653589793,0.0,2.910336527700544]),np.array([0.45133062093500004,0.125541410538,0.6469830730149999,-2.7789132350253714,-0.06440264939859076,-2.9866074160126965]),np.array([0.450000008512,0.0,0.46999999240199997,3.141592653589793,0.0,-3.141592653589793]),np.array([0.45000000915,-0.030243249899999998,0.469999991691,3.141592653589793,0.0,-3.141592653589793]),np.array([0.45000000679499996,0.052492723867999996,0.46999998589900005,3.141592653589793,0.0,3.141592653589793]),np.array([0.493088536067,0.052492720916000005,0.46999999003599996,-3.141592653589793,0.0,3.141592653589793])]
coords_list = [np.array([0.551377372112,0.0,0.647000003554,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.5516697665200001,0.157633351376,0.646999996348,-2.943846849338835,0.0,3.141592653589793]),np.array([0.5513773618410001,-0.168242049442,0.7603029467310001,-3.141592653589793,0.0,3.141592653589793]),np.array([0.496852655447,0.06202713065,0.587887151403,-3.141592653589793,0.0,3.141592653589793]),np.array([0.5767592708339999,0.0026559649259999996,0.73760776979,-1.7130406608324344,0.0,3.141592653589793]),np.array([0.5106230222170001,0.0,0.647000009727,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.38785909461699997,0.0,0.6470000065770001,-3.141592653589793,0.0,-3.141592653589793]),np.array([0.450000008384,0.036398472429,0.647000007402,3.141592653589793,0.0,-3.141592653589793]),np.array([0.450000008354,-0.052389891667999997,0.6470000073569999,-3.141592653589793,0.0,3.141592653589793]),np.array([0.450000012901,0.0,0.588588113076,3.141592653589793,0.0,-3.141592653589793]),np.array([0.450000008512,0.0,0.46999999240199997,3.141592653589793,0.0,-3.141592653589793]),np.array([0.45000000915,-0.030243249899999998,0.469999991691,3.141592653589793,0.0,-3.141592653589793]),np.array([0.45000000679499996,0.052492723867999996,0.46999998589900005,3.141592653589793,0.0,3.141592653589793]),np.array([0.493088536067,0.052492720916000005,0.46999999003599996,-3.141592653589793,0.0,3.141592653589793])]

i = 0
while robot.step(timestep) != -1:
    for coords in coords_list:
        print("Going to ", coords)
        # robot_inst, pose_values
        j_v = do_ik(robot_serial, coords)
        # robot_motors, joint_values
        move_motors(motors, j_v)
        # robot_sensors, joint_values
        if is_position_reached(sensors, j_v):
            camera.saveImage(chr(i+65) + '.png', 100) 
            i += 1
            continue
    break
print("Calibration photos are made.")


