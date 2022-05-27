import numpy as np
import cv2
import sys
import matplotlib.pyplot as plt


def getFovMask( gImg, erodeFlag = True, seSize = 10):
# %GETFOVMASK get a binary image of the Field of View mask '
# gImg: green challe uint8 image '
# erodeFlag: if set it will erode the mask '
    #Param '
    lowThresh = 0;
    if( len(sys.argv) < 3):
        seSize = 10
    histRes = np.histogram(gImg, range=(0,255))
    d = np.diff(histRes[0])
    lvlFound = np.argmax( d >= lowThresh)

    fovMask = ~ (gImg <= lvlFound)
    fovMask = np.array(fovMask, dtype=np.uint8)

    if len(sys.argv) > 1 and erodeFlag:

        #se = sk.morphology.disk(seSize)
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (seSize, seSize))
        #fovMask = sk.morphology.binary_erosion(fovMask,se)
        fovMask = cv2.erode(fovMask, se)
        #erode also borders '
        fovMask[0:seSize*2, :] = 0
        fovMask[:, 0:seSize*2] = 0
        #fovMask[-seSize*2:,-seSize*2:] = 0
        fovMask[-seSize*2:, :] = 0  #### THERE WAS A MISTAKE HERE.
        fovMask[:, -seSize*2:] = 0
        # plt.imshow(cv2.rotate(fovMask, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE))
        plt.imshow(fovMask,cmap="jet")
        plt.show()

    return fovMask
