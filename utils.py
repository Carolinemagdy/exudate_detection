import time
from skimage.morphology import reconstruction
import numpy as np
from scipy.signal import medfilt2d
import matplotlib.pyplot as plt

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


@timeit
def get_median_filt(img, newSize):
    #return np.double(median_filter(img, (round(newSize[0]/30), round(newSize[1]/30))))
    newSize = newSize[::-1]
    return np.double(medfilt2d(img, (round(newSize[0]/30), round(newSize[0]/30))))


@timeit
def get_reconstructed_bkg(img, medBg):
    maskImg = img
    pxLbl = maskImg < medBg
    maskImg[pxLbl] = medBg[pxLbl]
    return reconstruction(medBg.astype('uint8'), maskImg.astype('uint8'), method='dilation')


@timeit
def get_subtracted_img(img, medBg, imgFovMask):
    medRestored = get_reconstructed_bkg(np.double(img), medBg)
    subImg = np.double(img) - medRestored
    subImg = subImg * np.double(imgFovMask)
    subImg[subImg < 0] = 0
    return np.array(subImg > 0, dtype=np.uint8)


@timeit
def findGoodResolutionForWavelet(sizeIn):
    maxWavDecom = 2
    pxToAddC = 2**maxWavDecom - np.mod(sizeIn[1],2**maxWavDecom)
    pxToAddR = 2**maxWavDecom - np.mod(sizeIn[0],2**maxWavDecom)
    sizeOut =np.add(sizeIn,  [pxToAddR, pxToAddC])
    return sizeOut


@timeit
def plot_it(img, title):
    plt.figure(figsize=(10, 10))
    plt.title(title)
    plt.imshow(img)