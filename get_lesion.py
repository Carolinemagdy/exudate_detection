from scipy.misc import imresize
import scipy
import numpy as np


def  exDetect( rgbImgOrig, removeON, onY, onX ):

    # addpath('misc');

    #Parameters
    showRes = 0; # show lesions in image


    if nargin == 0:
        rgbImgOrig = imread( 'misc/img_ex_test.jpg' );
        removeON = 1;
        onY = 905;
        onX = 290;
        showRes = 1;

    imgProb = getLesions( rgbImgOrig, showRes, removeON, onY, onX );
    return imgProb


def getLesions( rgbImgOrig, showRes, removeON, onY, onX ):
    winOnRatio = [1/8,1/8]
    origSize = rgbImgOrig.shape
    newSize = [750,round(750*(origSize[2]/origSize[1]))]
    newSize = findGoodResolutionForWavelet(newSize)
    imgRGB = imresize(rgbImgOrig, newSize)
    imgG = imgRGB[:,:,2]
    import colorsys
    imgHSV = colorsys.rgb_to_hsv(imgRGB)
    imgV = imgHSV[:,:,3]
    imgV8 = np.uint8(imgV*255)
    if removeON:
        # get ON window
        onY = onY * newSize[1]/origSize[1]
        onX = onX * newSize[2]/origSize[2]
        onX = round(onX)
        onY = round(onY)
        winOnSize = round(winOnRatio*newSize)
        # remove ON window from imgTh
        winOnCoordY = [onY-winOnSize[1],onY+winOnSize[1]]
        winOnCoordX = [onX-winOnSize[2],onX+winOnSize[2]]
        if winOnCoordY[1] < 1:
            winOnCoordY[1] = 1
        if winOnCoordX[1] < 1:
            winOnCoordX[1] = 1
        if winOnCoordY[2] > newSize[1]:
            winOnCoordY[2] = newSize[1]
        if winOnCoordX[2] > newSize[2]:
            winOnCoordX[2] = newSize[2]
  
    imgFovMask = getFovMask( imgV8, 1, 30 )
    imgFovMask[winOnCoordY[1]:winOnCoordY[2], winOnCoordX[1]:winOnCoordX[2]] = 0
    
    medBg = float(scipy.signal.medfilt2d(imgV8, [round(newSize[1]/30),round(newSize[1]/30)]))
    #reconstruct bg
    maskImg = float(imgV8)
    pxLbl = maskImg < medBg
    maskImg[pxLbl] = medBg[pxLbl]
    medRestored = imreconstruct( medBg, maskImg )
    # subtract, remove fovMask and threshold
    subImg = float(imgV8) - float(medRestored)
    subImg = subImg* float(imgFovMask)
    subImg[subImg < 0] = 0
    imgThNoOD = np.uint8(subImg) > 0
    
    #Calculate edge strength of lesions
    imgKirsch = kirschEdges( imgG )
    img0 = imgG * np.uint8(imgThNoOD == 0)
    img0recon = imreconstruct(img0, imgG)
    img0Kirsch = kirschEdges(img0recon)
    imgEdgeNoMask = imgKirsch - img0Kirsch # edge strength map
    imgEdge = float(imgFovMask) * imgEdgeNoMask
    
    lesCandImg = np.zeros( newSize );
    lblImg = bwlabel(imgThNoOD,8);
    lesCand = regionprops(lblImg, 'PixelIdxList');
    for idxLes in range(len(lesCand)):
        pxIdxList = lesCand[idxLes].PixelIdxList;
        lesCandImg[pxIdxList] = sum(imgEdge[pxIdxList]) / len(pxIdxList);
    lesCandImg = imresize( lesCandImg, origSize(1:2), 'nearest' );
    
    # if( showRes ):
    #     figure(442);
    #     imagesc( rgbImgOrig );
    #     figure(446);
    #     imagesc( lesCandImg );     
           
    return lesCandImg

def findGoodResolutionForWavelet(sizeIn):
    maxWavDecom = 2;

    pxToAddC = 2^maxWavDecom - np.mod(sizeIn[2],2^maxWavDecom);
    pxToAddR = 2^maxWavDecom - np.mod(sizeIn[1],2^maxWavDecom);
    
    sizeOut = sizeIn + [pxToAddR, pxToAddC];
    return sizeOut

def  preprocessWavelet( imgIn, fovMask ):
    # Parameters
    maxWavDecom = 2;
    
    
    [imgA,imgH,imgV,imgD] = swt2( imgIn, maxWavDecom, 'haar' );
    imgRecon = iswt2( np.zeros(imgA[:,:,2].shape),imgH[:,:,2],imgV[:,:,2],imgD[:,:,2], 'haar' );

    imgRecon[imgRecon < 0] = 0;
    imgRecon = np.uint8( imgRecon );

    imgRecon = imgRecon*np.uint8(fovMask);
    imgOut = imgRecon * (255 / max(imgRecon[:]));
    return imgOut

def gauss1d( x, mu, sigma ):
    f = np.exp( -(x-mu)^2 / (2*sigma^2) ) / (sigma * sqrt(2*pi) );
    return f