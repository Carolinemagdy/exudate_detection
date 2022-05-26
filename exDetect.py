from cProfile import label
from tkinter import Label
from misc.getFovMask import get_fov_mask
from misc.KirschEdges import kirschEdges

import cv2
from cv2 import resize,imread
import numpy as np
import scipy
from scipy import signal
import skimage
from skimage import morphology, measure
def exDetect( rgbImgOrig, removeON=1, onY=905, onX=290 ):
    # exDetect: detect exudates
    #  V. 0.2 - 2010-02-01
    #  make compatible with Matlab2008
    #  V. 0.1 - 2010-02-01
    #           source: /mnt/data/ornl/lesions/exudatesCpp2/matlab/exudatesCpp3
    
    #-- Parameters
    showRes = 0; # show lesions in image
    #--
    # if no parameters are given use the test image
    if len(rgbImgOrig)==0 :
            showRes = 1
            exit('No image was selected')


    imgProb = getLesions( rgbImgOrig, removeON, onY, onX )
    return imgProb 

 
def getLesions( rgbImgOrig, removeON, onY, onX ):
    winOnRatio = [1/8,1/8]
    origSize = rgbImgOrig.shape
    newSize = [750,round(750*(origSize[1]/origSize[0]))]
    newSize = findGoodResolutionForWavelet(newSize)
    imgRGB = resize(rgbImgOrig, newSize)
    imgG = imgRGB[:,:,1]
    imgHSV = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)
    imgV = imgHSV[:,:,2]
    imgV8 = np.uint8(imgV*255)
    if removeON:
        # get ON window
        onY = onY * newSize[0]/origSize[0]
        onX = onX * newSize[1]/origSize[1]
        onX = round(onX)
        onY = round(onY)
        winOnSize = np.round(winOnRatio*newSize)
        # remove ON window from imgTh
        winOnCoordY = [onY-winOnSize[0],onY+winOnSize[0]]
        winOnCoordX = [onX-winOnSize[1],onX+winOnSize[1]]
        if winOnCoordY[0] < 1:
            winOnCoordY[0] = 1
        if winOnCoordX[0] < 1:
            winOnCoordX[0] = 1
        if winOnCoordY[1] > newSize[0]:
            winOnCoordY[1] = newSize[0]
        if winOnCoordX[1] > newSize[1]:
            winOnCoordX[1] = newSize[1]
  
    imgFovMask = get_fov_mask( imgV8, 1, 30 )
    import matplotlib.pyplot as plt
    plt.imshow(imgFovMask)
    plt.show()
    imgFovMask[int(winOnCoordY[0]):int(winOnCoordY[1]), int(winOnCoordX[0]):int(winOnCoordX[1])] = 0
    
    medBg = signal.medfilt2d(imgV8, kernel_size=round(newSize[0]/30))
    medBg=medBg.astype(np.float)
    #reconstruct bg
    maskImg = imgV8.astype(np.float)
    pxLbl = maskImg < medBg
    maskImg[pxLbl] = medBg[pxLbl]
    medRestored = skimage.morphology.reconstruction( medBg, maskImg )
    # subtract, remove fovMask and threshold
    bgFloat=medBg.astype(np.float)
    resFloat=medRestored.astype(np.float)
    subImg = bgFloat - resFloat
    maskFloat=imgFovMask.astype(np.float)
    subImg = subImg* maskFloat
    subImg[subImg < 0] = 0
    imgThNoOD = np.uint8(subImg) > 0
    
    #Calculate edge strength of lesions
    imgKirsch = kirschEdges( imgG )
    img0 = imgG * np.uint8(imgThNoOD == 0)
    img0recon = morphology.reconstruction(img0, imgG)
    img0Kirsch = kirschEdges(img0recon)
    imgEdgeNoMask = imgKirsch - img0Kirsch # edge strength map
    imgEdge = maskFloat* imgEdgeNoMask
    
    lesCandImg = np.zeros( newSize )
    print(lesCandImg.shape)
    lblImg = measure.label(imgThNoOD,connectivity=2)
    lesCand = measure.regionprops(lblImg)
    for idxLes in range(len(lesCand)):
        pxIdxList = lesCand[idxLes]
        lesCandImg[pxIdxList] = sum(imgEdge[pxIdxList]) / len(pxIdxList)
    lesCandImg = resize( lesCandImg, origSize[0:2] )
    
    # if( showRes ):
    #     figure(442);
    #     imagesc( rgbImgOrig );
    #     figure(446);
    #     imagesc( lesCandImg );     
           
    return lesCandImg

def findGoodResolutionForWavelet(sizeIn):
    maxWavDecom = 2
    pxToAddC = 2**maxWavDecom - np.mod(sizeIn[1],2**maxWavDecom)
    pxToAddR = 2**maxWavDecom - np.mod(sizeIn[0],2**maxWavDecom)
    sizeOut =np.add(sizeIn,  [pxToAddR, pxToAddC])  
    return sizeOut 
