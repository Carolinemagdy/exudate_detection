import numpy as np
import cv2
import sys



def getFovMask( gImg, erodeFlag = True, seSize = 10):

    lowThresh = 0;
    histRes = np.histogram(gImg, range=(0,255))
    d = np.diff(histRes[0])
    lvlFound = np.argmax( d >= lowThresh)

    fovMask = ~ (gImg <= lvlFound)
    fovMask = np.array(fovMask, dtype=np.uint8)

    if len(sys.argv) > 1 and erodeFlag:


        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (seSize, seSize))

        fovMask = cv2.erode(fovMask, se)

        fovMask[0:seSize*2, :] = 0
        fovMask[:, 0:seSize*2] = 0
        fovMask[-seSize*2:, :] = 0  
        fovMask[:, -seSize*2:] = 0


    return fovMask
