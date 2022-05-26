import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import skimage.morphology
import re
from scipy import ndimage
from skimage.measure import regionprops, label
import time
import scipy


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
def load_images(image_dir):
    im_list = []
    rows, cols = [], []
    for file in glob.glob(os.path.join(image_dir, "*.jpg")):

        im = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        if im is not None:
            im_list.append(im)

    for file in glob.glob(os.path.join(image_dir, "*.meta")):
        meta = open(file, 'r')
        for line in meta:
            rows.append(re.findall("ONrow\W+([0-9\.]+)", line))
            cols.append(re.findall("ONcol\W+([0-9\.]+)", line))

    rows_locs = list(filter(lambda x: x, rows))
    cols_locs = list(filter(lambda x: x, cols))
    rows_locs = [int(s[0]) for s in rows_locs]
    cols_locs = [int(s[0]) for s in cols_locs]

    nerve_locs = list(zip(rows_locs, cols_locs))

    return im_list, nerve_locs



@timeit
def median_filter(img):
    ksize = int(img.shape[0] / 30)
    kernel_size = (ksize if ksize % 2 == 1 else ksize + 1)
    filtered_img = cv2.medianBlur(img, ksize=kernel_size)
    return filtered_img


@timeit
def morphological_reconstruction(filter_img, scale_img):
    # print(scale_img.shape, "scale")
    # print(filter_img.shape, "filter")
    # mask = cv2.max(filter_img, scale_img)
    return skimage.morphology.reconstruction(filter_img, scale_img)


@timeit
def imreconstruct(marker: np.ndarray, mask: np.ndarray, radius: int = 1):
    """Iteratively expand the markers white keeping them limited by the mask during each iteration.
    :param marker: Grayscale image where initial seed is white on black background.
    :param mask: Grayscale mask where the valid area is white on black background.
    :param radius Can be increased to improve expansion speed while causing decreased isolation from nearby areas.
    :returns A copy of the last expansion.
    Written By Semnodime.
    """

    kernel = np.ones(shape=(radius * 2 + 1,) * 2, dtype=np.uint8)
    while True:
        expanded = cv2.dilate(src=marker, kernel=kernel)
        cv2.bitwise_and(src1=expanded, src2=mask, dst=expanded)

        # Termination criterion: Expansion didn't change the image at all
        if (marker == expanded).all():
            return expanded
        marker = expanded


@timeit
def get_lesions(img, nerve_x, nerve_y):
    old_shape = img.shape
    scale = 752 / 2196
    dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
    # new_shape = scale * img.shape
    new_shape = dim
    scaled_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    nerve_x = np.round(scale * nerve_x)
    nerve_y = np.round(scale * nerve_y)
    win_ratio = np.array([1 / 8, 1 / 8])
    win_size = np.round(win_ratio * scale)
    win_x = [(nerve_x - win_size[0] if (nerve_x - win_size[0]) >= 1 else 1),
             (nerve_x + win_size[0] if (nerve_x + win_size[0]) < new_shape[0] else new_shape[0] - 1)]
    win_y = [(nerve_y - win_size[1] if (nerve_y - win_size[1]) >= 1 else 1),
             (nerve_y + win_size[1] if (nerve_y + win_size[1]) < new_shape[1] else new_shape[1] - 1)]
    im_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(im_hsv)
    hsv_img = v
    hsv_img = np.array(hsv_img * 255, dtype=np.uint8)
    img_fov_mask = get_fov_mask(hsv_img, 1, 30)
    win_x = np.array(win_x, dtype=np.uint8)
    win_y = np.array(win_y, dtype=np.uint8)
    img_fov_mask[win_x[0]:win_x[1], win_y[0]:win_y[1]] = 0
    med_bg = median_filter(hsv_img)
    mask_img = np.array([hsv_img < med_bg], dtype=np.int8)
    mask_img = mask_img.reshape((mask_img.shape[1], mask_img.shape[2]))
    med_restored = imreconstruct(med_bg.astype('uint8'), mask_img.astype('uint8'))

    sub_img = hsv_img - med_restored

    sub_img = sub_img * img_fov_mask
    sub_img[sub_img < 0] = 0
    img_th_nod = np.uint8(sub_img) > 0
    r, g, b = cv2.split(img)
    img_green = g
    img_kirsch = kirsch(img_green)
    img0 = img_green * np.uint8(img_th_nod == 0)
    img_0_recon = imreconstruct(img0, img_green)
    img0_kirsch = kirsch(img_0_recon)
    img_edge_no_mask = img_kirsch - img0_kirsch
    img_edge = img_fov_mask * img_edge_no_mask
    #lblImg = ndimage.label(img_th_nod, structure=np.ones((3, 3)))[0]
    lesCand = scipy.ndimage.measurements.label(img_th_nod)[0]
    lesCandImg = np.zeros(new_shape)
    print("Started Timing!")
    t1 = time.perf_counter()
    for idxLes in range(lesCand.max()):
        pxIdxList = lesCand[lesCand == idxLes].flatten()
        lesCandImg[pxIdxList] = np.sum(img_edge[pxIdxList]) / len(pxIdxList)
    t2 = time.perf_counter()
    print("Finished Timing!")
    print("Time Elapsed: ", t2 - t1)
    print("old shape: ", old_shape[0:2])
    les_cand_img = cv2.resize(lesCandImg, old_shape[0:2], interpolation=cv2.INTER_AREA)

    plt.imshow(les_cand_img, cmap='gray')
    plt.show()


# def resolution_for_wavelet(size_in):
#     max_wave_decom = 2
#     px_add_c = 2 ** max_wave_decom - np.mod(size_in[1], 2 ** max_wave_decom)
#     px_add_r = 2 ** max_wave_decom - np.mod(size_in[0], 2 ** max_wave_decom)
#     return size_in + [px_add_c, px_add_r]
#
#
# def preprocess_wavelet(img_in, fov_mask):
#     max_wave_decom = 2