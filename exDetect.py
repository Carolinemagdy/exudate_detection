import imp
import cv2
from cv2 import resize
import numpy as np
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
        #try,Except
        showRes = 1;

    imgProb = getLesions( rgbImgOrig, showRes, removeON, onY, onX )
    return imgProb 


def getLesions( rgbImgOrig, showRes, removeON, onY, onX ):
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
  
    # imgFovMask = getFovMask( imgV8, 1, 30 )
    # imgFovMask[winOnCoordY[1]:winOnCoordY[2], winOnCoordX[1]:winOnCoordX[2]] = 0
    
    # medBg = float(scipy.signal.medfilt2d(imgV8, [round(newSize[1]/30),round(newSize[1]/30)]))
    # #reconstruct bg
    # maskImg = float(imgV8)
    # pxLbl = maskImg < medBg
    # maskImg[pxLbl] = medBg[pxLbl]
    # medRestored = imreconstruct( medBg, maskImg )
    # # subtract, remove fovMask and threshold
    # subImg = float(imgV8) - float(medRestored)
    # subImg = subImg* float(imgFovMask)
    # subImg[subImg < 0] = 0
    # imgThNoOD = np.uint8(subImg) > 0
    
    # #Calculate edge strength of lesions
    # imgKirsch = kirschEdges( imgG )
    # img0 = imgG * np.uint8(imgThNoOD == 0)
    # img0recon = imreconstruct(img0, imgG)
    # img0Kirsch = kirschEdges(img0recon)
    # imgEdgeNoMask = imgKirsch - img0Kirsch # edge strength map
    # imgEdge = float(imgFovMask) * imgEdgeNoMask
    
    # lesCandImg = np.zeros( newSize );
    # lblImg = bwlabel(imgThNoOD,8);
    # lesCand = regionprops(lblImg, 'PixelIdxList');
    # for idxLes in range(len(lesCand)):
    #     pxIdxList = lesCand[idxLes].PixelIdxList;
    #     lesCandImg[pxIdxList] = sum(imgEdge[pxIdxList]) / len(pxIdxList);
    # lesCandImg = imresize( lesCandImg, origSize(1:2), 'nearest' );
    
    # if( showRes ):
    #     figure(442);
    #     imagesc( rgbImgOrig );
    #     figure(446);
    #     imagesc( lesCandImg );     
           
    # return lesCandImg

def findGoodResolutionForWavelet(sizeIn):
    maxWavDecom = 2
    pxToAddC = 2**maxWavDecom - np.mod(sizeIn[1],2**maxWavDecom)
    pxToAddR = 2**maxWavDecom - np.mod(sizeIn[0],2**maxWavDecom)
    sizeOut =np.add(sizeIn,  [pxToAddR, pxToAddC])  
    return sizeOut 
