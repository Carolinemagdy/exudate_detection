import time
from skimage.morphology import reconstruction
import numpy as np
import matplotlib.pyplot as plt
import cv2


def timeit(method):
    """
    Decorator to time a function
    :param method: the function to time
    :return: print the time it took to run the function
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' %
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


@timeit
def get_median_filter(img, new_size):
    """
    a function to get a median filter of a given size
    :param img: the image to filter
    :param new_size: the size of the filter
    :return: filtered image
    """
    new_size = new_size[::-1]
    # return medfilt2d(img, (round(new_size[0]/30), round(new_size[0]/30)))
    return cv2.medianBlur(img, round(new_size[0] / 30))  # 14 times faster


@timeit
def get_reconstructed_bkg(img, med_bg):
    """
    a function to perform a reconstruction of the background
    :param img: the image to reconstruct
    :param med_bg: the median background
    :return: reconstructed image
    """
    maskImg = img
    pxLbl = maskImg < med_bg
    maskImg[pxLbl] = med_bg[pxLbl]
    return reconstruction(med_bg.astype('uint8'), maskImg.astype('uint8'), method='dilation')


@timeit
def get_subtracted_img(img, med_bg, img_fov_mask):
    """
    a function to perform morphological reconstruction for the median background then subtract the background
     from the image
    :param img: image to subtract background from
    :param med_bg: the median background
    :param img_fov_mask: the mask of the image
    :return: boolean array of the difference between the image and the background where the difference is greater than 0
    """
    medRestored = get_reconstructed_bkg(np.double(img), med_bg)
    subImg = np.double(img) - medRestored
    subImg = subImg * np.double(img_fov_mask)
    subImg[subImg < 0] = 0
    return np.array(subImg > 0, dtype=np.uint8)


@timeit
def find_good_resolution_for_wavelet(size_in):
    """
    a function to find the best resolution for the wavelet transform
    :param size_in: the original size of the image
    :return: the best resolution for the wavelet transform
    """
    max_wav_decom = 2
    px_to_add_c = 2 ** max_wav_decom - np.mod(size_in[1], 2 ** max_wav_decom)
    px_to_add_r = 2 ** max_wav_decom - np.mod(size_in[0], 2 ** max_wav_decom)
    size_out = np.add(size_in, [px_to_add_r, px_to_add_c])
    return size_out


@timeit
def plot_it(img, title):
    """
    a function to plot an image while experimenting
    :param img: the image to be plotted
    :param title: the title of the figure to be plotted
    :return: None
    """
    plt.figure(figsize=(10, 10))
    plt.title(title)
    plt.imshow(img)
