import 
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
    if rgbImgOrig is not None :
        rgbImgOrig = imread( 'misc/img_ex_test.jpg' );
        showRes = 1;

    imgProb = getLesions( rgbImgOrig, showRes, removeON, onY, onX )
    return imgProb 


def getLesions():
    