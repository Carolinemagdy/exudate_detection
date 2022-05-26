import numpy as np
import cv2


def get_fov_mask(img, erode_flag, se_size=10):
    lower_thresh = 0
    w, t = np.histogram(img, range=(0, 255))
    difference = np.diff(w)
    level_found = np.argwhere(difference >= lower_thresh)[0]
    fov_mask = np.invert(img <= level_found)
    fov_mask = np.array(fov_mask, dtype=np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (se_size, se_size))
    eroded_img = cv2.erode(fov_mask, kernel)
    eroded_img[1:se_size * 2, :] = 0
    eroded_img[:, 1:se_size * 2] = 0
    eroded_img[-se_size * 2:, :] = 0
    eroded_img[:, -se_size * 2:] = 0
    return eroded_img
