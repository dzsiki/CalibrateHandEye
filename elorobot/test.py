import cv2
import cv2 as cv
import numpy as np
import pyikfast_irb140 as ik
import math
from scipy.spatial.transform import Rotation as R

asd = ik.forward([0,0,0,0,math.pi/2,0])
print(asd)
print(R.from_matrix(np.array(asd[1]).reshape(3,3)).as_euler('zyx',degrees=True))





'''
CHECKERBOARD_WIDTH = 14
CHECKERBOARD_HEIGHT = 9

def prepareimage(img):
    lwr = np.array([0, 0, 9])
    upr = np.array([255, 200, 100])
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    msk = cv.inRange(hsv, lwr, upr)

    # Élsimítás hozzáadása
    msk = cv.GaussianBlur(msk, (7, 7), 0)

    # Kernel méretének növelése
    krn = cv.getStructuringElement(cv.MORPH_RECT, (70, 50))

    # Dilatáció iterációinak növelése
    dlt = cv.dilate(msk, krn, iterations=0)
    res = 255 - cv.bitwise_and(dlt, msk)
    return np.uint8(res)

img = cv.imread("~Y.png")
imgbw = prepareimage(img)
ret, corners = cv.findChessboardCornersSB(imgbw, (CHECKERBOARD_HEIGHT, CHECKERBOARD_WIDTH), None)
print(ret)
imgbw=cv.resize(imgbw,(1024,768))
cv2.imshow("asd",imgbw)
cv.waitKey()
'''
