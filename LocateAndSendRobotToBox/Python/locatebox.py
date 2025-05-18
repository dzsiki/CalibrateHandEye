import pickle
import numpy as np
import cv2 as cv

CHECKERBOARD_WIDTH = 3
CHECKERBOARD_HEIGHT = 3
SQUARE_SIZE = 7.5
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


cap = cv.VideoCapture(1, cv.CAP_DSHOW)

rot, pose = [-1.0, -1.2246063538223773e-16, 1.4996607218221374e-32, -1.2246063538223773e-16, 1.0, -1.2246063538223773e-16, 0.0, -1.2246063538223773e-16, -1.0], [465,0,577]

file = open('mtx.txt', 'rb')
mtx = pickle.load(file)
file.close()
file = open('dist.txt', 'rb')
dist = pickle.load(file)
file.close()
file = open('R_cam2gripper.txt', 'rb')
R_cam2gripper = pickle.load(file)
file.close()
file = open('t_cam2gripper.txt', 'rb')
t_cam2gripper = pickle.load(file)
file.close()

def objpgen(middle):
    objp = np.zeros((CHECKERBOARD_HEIGHT * CHECKERBOARD_WIDTH, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD_HEIGHT, 0:CHECKERBOARD_WIDTH].T.reshape(-1, 2)

    if middle:
        for i in range(len(objp)):
            objp[i][0] -= (CHECKERBOARD_HEIGHT - 1) / 2
            objp[i][1] -= (CHECKERBOARD_WIDTH - 1) / 2

    objp *= SQUARE_SIZE*-1
    return objp

def prepareimage(img):
    lwr = np.array([0, 0, 9])
    upr = np.array([255, 200, 100])
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    msk = cv.inRange(hsv, lwr, upr)
    msk = cv.GaussianBlur(msk, (9, 9), 0)
    krn = cv.getStructuringElement(cv.MORPH_RECT, (70, 50))
    dlt = cv.dilate(msk, krn, iterations=10)
    res = 255 - cv.bitwise_and(dlt, msk)
    return np.uint8(res)

def worldposecalc(img, middle, mtx, dist, R_base2gripper, t_base2gripper, R_cam2gripper, t_cam2gripper):
    objp = objpgen(middle)

    # the position from the Robotstudio (same as the real on the pendant)
    R_base2gripper = np.array([[R_base2gripper[0], R_base2gripper[1], R_base2gripper[2]],
                               [R_base2gripper[3], R_base2gripper[4], R_base2gripper[5]],
                               [R_base2gripper[6], R_base2gripper[7], R_base2gripper[8]]])
    t_base2gripper = np.array([[t_base2gripper[0]], [t_base2gripper[1]], [t_base2gripper[2]]])

    imgbw = prepareimage(img)
    #ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)
    ret, corners = cv.findChessboardCorners(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)

    if not ret:
        print("No checkerboard.")
        return None,None

    corners2 = cv.cornerSubPix(imgbw, corners, (11, 11), (-1, -1), criteria)
    # Find the rotation and translation vectors for object to the camera
    ret, R_object2cam, t_object2cam = cv.solvePnP(objp, corners2, mtx, dist)

    img = cv.drawFrameAxes(img, mtx, dist, R_object2cam, t_object2cam, SQUARE_SIZE * 3, 3)
    cv.imshow('Pose', img)

    R_object2cam, _ = cv.Rodrigues(R_object2cam, np.eye(3))

    # combine the rot and trans to 4x4 matrix
    base2gripper = np.vstack((np.hstack((R_base2gripper, (t_base2gripper).flatten()[:, None])), [0, 0, 0, 1]))

    cam2gripper = np.vstack((np.hstack((R_cam2gripper, (t_cam2gripper).flatten()[:, None])), [0, 0, 0, 1]))

    object2cam = np.vstack((np.hstack((R_object2cam, (t_object2cam).flatten()[:, None])), [0, 0, 0, 1]))

    # get the base to object rot and trans
    base2object = np.dot(base2gripper, np.dot(cam2gripper, object2cam))

    R_base2object = base2object[:3, :3]
    t_base2object = base2object[:3, 3].tolist()
    return R_base2object, t_base2object

while(True):
    ret, frame = cap.read()
    if ret:
        R_base2object, t_base2object = worldposecalc(frame, True, mtx, dist, rot,
                                                             pose, R_cam2gripper, t_cam2gripper)
        if(t_base2object is not None):
            print(t_base2object)
        cv.waitKey(1000)