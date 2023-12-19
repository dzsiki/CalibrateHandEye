import cv2 as cv
import numpy as np
import glob

CHECKERBOARD_WIDTH = 9
CHECKERBOARD_HEIGHT = 14
SQUARE_SIZE = 0.02576
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def objpgen(middle):
    objp = np.zeros((CHECKERBOARD_HEIGHT * CHECKERBOARD_WIDTH, 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD_HEIGHT, 0:CHECKERBOARD_WIDTH].T.reshape(-1, 2)

    if middle:
        for i in range(len(objp)):
            objp[i][0] -= (CHECKERBOARD_HEIGHT - 1) / 2
            objp[i][1] -= (CHECKERBOARD_WIDTH - 1) / 2

    objp *= SQUARE_SIZE
    return objp


def prepareimage(img):
    lwr = np.array([0, 0, 0])
    upr = np.array([255, 100, 150])
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    msk = cv.inRange(hsv, lwr, upr)
    krn = cv.getStructuringElement(cv.MORPH_RECT, (50, 30))
    dlt = cv.dilate(msk, krn, iterations=5)
    res = 255 - cv.bitwise_and(dlt, msk)
    return np.uint8(res)


# === CALIBRATE CAMERA ============================================================================

def calibrate(middle):
    # Prepare object points
    objp = objpgen(middle)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

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

    # Obtain camera parameters
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, imgbw.shape[::-1], None, None)
    print(tvecs)
    return ret, mtx, dist, rvecs, tvecs


# === FIND POSE OF TARGETS ===========================================================================
def findpose(middle, camerat, camerar):
    rvecsarray = []
    tvecsarray = []
    R_gripper2base = []
    T_gripper2base = []

    ret, mtx, dist, rvecs, tvecs = calibrate(middle)
    # Prepare object points
    objp = objpgen(middle)

    images = [img for img in glob.glob('*.png') if not img.startswith('~')]
    for idx, fname in enumerate(images):
        img = cv.imread(fname)
        imgbw = prepareimage(img)
        ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH ), None)
        if ret:

            corners2 = cv.cornerSubPix(imgbw, corners, (11, 11), (-1, -1), criteria)
            # Find the rotation and translation vectors.
            ret, rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)

            img = cv.drawFrameAxes(img, mtx, None, rvecs, tvecs, SQUARE_SIZE, 3)
            cv.imshow('Pose', img)
            cv.waitKey()

            R_gripper2base.append(np.array([[camerar[idx][0], camerar[idx][1], camerar[idx][2]],
                                            [camerar[idx][3], camerar[idx][4], camerar[idx][5]],
                                            [camerar[idx][6], camerar[idx][7], camerar[idx][8]]]))
            T_gripper2base.append(np.array([[camerat[idx][0]], [camerat[idx][1]], [camerat[idx][2]]]))

            rmatrix, _ = cv.Rodrigues(rvecs, np.eye(3))
            rvecsarray.append(rmatrix)
            tvecsarray.append(tvecs)

    R_cam2gripper, t_cam2gripper = cv.calibrateHandEye(R_gripper2base, T_gripper2base,
                                                       rvecsarray, tvecsarray)
    return mtx, None, R_cam2gripper, t_cam2gripper
