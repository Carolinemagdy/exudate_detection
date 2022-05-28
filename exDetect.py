from misc.getFovMask import getFovMask
from misc.KirschEdges import kirschEdges
from utils import *
import cv2
from cv2 import resize
import numpy as np
import scipy
from skimage.morphology import reconstruction


def exDetect(rgbImgOrig, removeON=1, onY=905, onX=290):
    if len(rgbImgOrig) == 0:
            showRes = 1
            exit('No image was selected')

    imgProb = getLesions(rgbImgOrig, removeON, onY, onX)
    return imgProb 


def getLesions(rgbImgOrig, removeON, onY, onX):
    winOnRatio = [1/8, 1/8]

    origSize = rgbImgOrig.shape

    newSize = np.array([750, round(750*(origSize[1]/origSize[0]))])

    newSize = findGoodResolutionForWavelet(newSize)

    newSize = newSize[::-1]

    imgRGB = resize(rgbImgOrig, newSize, interpolation=cv2.INTER_AREA)

    imgG = imgRGB[:, :, 1]

    imgHSV = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)

    imgV = imgHSV[:, :, 2]

    imgV8 = np.uint8(imgV)
    if removeON:
        # get ON window
        onY = np.round(onY * newSize[1]/origSize[1])
        onX = np.round(onX * newSize[0]/origSize[0])

        winOnSize = np.round(winOnRatio*newSize)
        # remove ON window from imgTh
        winOnCoordY = [onY-winOnSize[1], onY+winOnSize[1]]
        winOnCoordX = [onX-winOnSize[0], onX+winOnSize[0]]

        if winOnCoordY[0] < 0:
            winOnCoordY[0] = 0
        if winOnCoordX[0] < 0:
            winOnCoordX[0] = 0
        if winOnCoordY[1] > newSize[0]:
            winOnCoordY[1] = newSize[0]
        if winOnCoordX[1] > newSize[1]:
            winOnCoordX[1] = newSize[1]

    winOnCoordX = np.array(winOnCoordX, dtype=np.int16)
    winOnCoordY = np.array(winOnCoordY, dtype=np.int16)

    imgFovMask = getFovMask(imgV8, 1, 30)
    imgFovMask[winOnCoordY[0]:winOnCoordY[1], winOnCoordX[0]:winOnCoordX[1]] = 0
    imgFovMask = imgFovMask.astype(np.uint8)

    medBg = get_median_filt(imgV8, newSize)

    imgThNoOD = get_subtracted_img(imgV8, medBg, imgFovMask)

    imgKirsch = kirschEdges(imgG)

    img0 = imgG * np.uint8(imgThNoOD == 0)

    img0recon = reconstruction(img0, imgG)

    img0Kirsch = kirschEdges(img0recon)

    imgEdgeNoMask = imgKirsch - img0Kirsch

    plot_it(imgEdgeNoMask, 'imgEdgeNoMask')
    imgEdge = imgFovMask * imgEdgeNoMask
    plot_it(imgEdge, 'imgEdge')
    lesCandImg = np.zeros(newSize[::-1])


    lesCand = scipy.ndimage.measurements.label(imgThNoOD, structure=np.ones((3,3)))[0]
    for idxLes in range(lesCand.max()):
        pxIdxList = lesCand == idxLes
        lesCandImg[pxIdxList] = np.sum(imgEdge[pxIdxList]) / pxIdxList.sum()

    lesCandImg = cv2.resize(lesCandImg, origSize[:2][::-1], interpolation=cv2.INTER_AREA)
    plot_it(lesCandImg, 'lesCandImg')
    return lesCandImg


