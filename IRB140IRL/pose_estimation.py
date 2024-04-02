import cv2
import cv2 as cv
import numpy as np
import glob
from scipy.spatial.transform import Rotation as R

np.set_printoptions(suppress=True)

CHECKERBOARD_WIDTH = 14
CHECKERBOARD_HEIGHT = 9
SQUARE_SIZE = 11
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# generate the objp array. if the param is true, the middle of the checkerboard should be the 0,0 else the top right corner
def objpgen(middle):
    objp = np.zeros((CHECKERBOARD_HEIGHT * CHECKERBOARD_WIDTH, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD_HEIGHT, 0:CHECKERBOARD_WIDTH].T.reshape(-1, 2)

    if middle:
        for i in range(len(objp)):
            objp[i][0] -= (CHECKERBOARD_HEIGHT - 1) / 2
            objp[i][1] -= (CHECKERBOARD_WIDTH - 1) / 2

    objp *= SQUARE_SIZE*-1
    return objp

#make the image better for finding corners
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


# === CALIBRATE CAMERA ============================================================================

def calibrate(middle):
    # Prepare object points
    objp = objpgen(middle)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    # find chessboard for all png except if it starts with ~
    images = [img for img in glob.glob('*.png') if not img.startswith('~')]
    # Process the images
    for fname in images:
        img = cv.imread(fname)
        imgbw = prepareimage(img)
        # Find the chess board corners
        ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)
        # If found, add object points, image points (after refining them)
        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)
        else:
            print(fname)
            imgbw= cv2.resize(imgbw,(1024,768))
            img= cv2.resize(img,(1024,768))
            cv.imshow(fname,imgbw)
            cv.imshow("asd",img)
            cv.waitKey()

    # Obtain camera parameters
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, imgbw.shape[::-1], None, None)

    return ret, mtx, dist, rvecs, tvecs


# === FIND POSE OF TARGETS ===========================================================================
def findpose(middle, camerat, camerar):
    rvecsarray = []
    tvecsarray = []
    #it's propably base2gripper?
    R_gripper2baseArray = []
    T_gripper2baseArray = []

    ret, mtx, dist, rvecs, tvecs = calibrate(middle)
    # Prepare object points
    objp = objpgen(middle)

    images = [img for img in glob.glob('*.png') if not img.startswith('~')]
    for idx, fname in enumerate(images):
        img = cv.imread(fname)
        imgbw = prepareimage(img)
        ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)
        if ret:

            corners2 = cv.cornerSubPix(imgbw, corners, (11, 11), (-1, -1), criteria)
            # Find the rotation and translation vectors.
            ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)

            # with this i got a relatable translation but weird 70 70 70 rotation
            R_gripper2baseArray.append(np.array([[camerar[idx][0], camerar[idx][1], camerar[idx][2]],
                                            [camerar[idx][3], camerar[idx][4], camerar[idx][5]],
                                            [camerar[idx][6], camerar[idx][7], camerar[idx][8]]]))
            t_g2b = camerat[idx]

            '''Also tried because the calibrateHandEye's paramater's name is gripper2base:
            With this i got a nice 90°angle but then the translations are way off
            
            R_gripper2baseArray.append(np.array([[camerar[idx][0], camerar[idx][1], camerar[idx][2]],
                                            [camerar[idx][3], camerar[idx][4], camerar[idx][5]],
                                            [camerar[idx][6], camerar[idx][7], camerar[idx][8]]]).T)
            t_g2b = -R_gripper2baseArray[idx] @ camerat[idx]
            '''


            T_gripper2baseArray.append(np.array([[t_g2b[0]], [t_g2b[1]], [t_g2b[2]]]))

            rmatrix, _ = cv.Rodrigues(rvecs, np.eye(3))
            rvecsarray.append(rmatrix)
            tvecsarray.append(tvecs)

    # get the rotation and translation vectors for cam to the gripper
    R_cam2gripper, t_cam2gripper = cv.calibrateHandEye(R_gripper2baseArray, T_gripper2baseArray,
                                                       rvecsarray, tvecsarray)
    return mtx, dist, R_cam2gripper, t_cam2gripper

# try to calculate the word coordinate of the object
def worldposecalc(fname, middle, mtx, dist, R_base2gripper, t_base2gripper, R_cam2gripper, t_cam2gripper):
    objp = objpgen(middle)

    # the position from the Robotstudio (same as the real on the pendant)
    R_base2gripper = np.array([[R_base2gripper[0], R_base2gripper[1], R_base2gripper[2]],
                               [R_base2gripper[3], R_base2gripper[4], R_base2gripper[5]],
                               [R_base2gripper[6], R_base2gripper[7], R_base2gripper[8]]])
    t_base2gripper = np.array([[t_base2gripper[0]], [t_base2gripper[1]], [t_base2gripper[2]]])

    img = cv.imread(fname)
    imgbw = prepareimage(img)
    ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)

    if not ret:
        print("No checkerboard.")
        return

    corners2 = cv.cornerSubPix(imgbw, corners, (11, 11), (-1, -1), criteria)
    # Find the rotation and translation vectors for object to the camera
    ret, R_object2cam, t_object2cam = cv.solvePnP(objp, corners2, mtx, dist)

    img = cv.drawFrameAxes(img, mtx, None, R_object2cam, t_object2cam, SQUARE_SIZE, 3)
    cv.imshow('Pose', img)
    cv.waitKey()

    R_object2cam, _ = cv.Rodrigues(R_object2cam, np.eye(3))

    # combine the rot and trans to 4x4 matrix
    base2gripper = np.vstack((np.hstack((R_base2gripper, (t_base2gripper).flatten()[:, None])), [0, 0, 0, 1]))

    cam2gripper = np.vstack((np.hstack((R_cam2gripper, (t_cam2gripper).flatten()[:, None])), [0, 0, 0, 1]))

    object2cam = np.vstack((np.hstack((R_object2cam, (t_object2cam).flatten()[:, None])), [0, 0, 0, 1]))

    # get the base to object rot and trans
    base2object = np.dot(base2gripper, np.dot(cam2gripper, object2cam))


    print("base to gripper:")
    print(t_base2gripper)
    print(R.from_matrix(R_base2gripper).as_euler('xyz',degrees=True))
    print("cam to gripper:")
    print(t_cam2gripper)
    print(R.from_matrix(R_cam2gripper).as_euler('xyz',degrees=True))
    print("Object to cam:")
    print(t_object2cam)
    print(R.from_matrix(R_object2cam).as_euler('xyz',degrees=True))

    R_base2object = base2object[:3, :3].flatten().tolist()
    t_base2object = base2object[:3, 3].tolist()
    return R_base2object, t_base2object
