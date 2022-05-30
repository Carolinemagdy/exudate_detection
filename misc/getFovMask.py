import numpy as np
import cv2
from utils import timeit


@timeit
def get_fov_mask(g_img, se_size=10):
    """
    Get the field of view mask.
    :param g_img: the green channel image
    :param se_size: the size of the structuring element
    :return: the field of view mask
    """
    lowThresh = 0
    histRes = np.histogram(g_img, range=(0, 255))
    d = np.diff(histRes[0])
    lvlFound = np.argmax(d >= lowThresh)

    fov_mask = ~ (g_img <= lvlFound)
    fov_mask = np.array(fov_mask, dtype=np.uint8)

    se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (se_size, se_size))

    fov_mask = cv2.erode(fov_mask, se)

    fov_mask[0:se_size*2, :] = 0
    fov_mask[:, 0:se_size*2] = 0
    fov_mask[-se_size*2:, :] = 0  
    fov_mask[:, -se_size*2:] = 0

    return fov_mask
