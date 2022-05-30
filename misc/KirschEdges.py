import numpy as np
import cv2
from utils import timeit


@timeit
def kirsch_edges(img):
    """
    function to detect edges using Kirsch operator
    :param img: the 2-D image to detect edges on
    :return: the image with edges detected
    """
    if img.ndim > 2:
        raise Exception("Image should be 2-D.")
    kernel_g1 = np.array([[5, -3, -3],
                         [5, 0, -3],
                         [5, -3, -3]], dtype=np.float32) / 15

    kernel_g2 = np.array([[-3, -3, 5],
                         [-3, 0, 5],
                         [-3, -3, 5]], dtype=np.float32) / 15

    kernel_g3 = np.array([[-3, -3, -3],
                         [5, 0, -3],
                         [5, 5, -3]], dtype=np.float32) / 15

    kernel_g4 = np.array([[-3, 5, 5],
                         [-3, 0, 5],
                         [-3, -3, -3]], dtype=np.float32) / 15

    kernel_g5 = np.array([[-3, -3, -3],
                         [-3, 0, -3],
                         [5, 5, 5]], dtype=np.float32) / 15

    kernel_g6 = np.array([[5, 5, 5],
                         [-3, 0, -3],
                         [-3, -3, -3]], dtype=np.float32) / 15

    kernel_g7 = np.array([[-3, -3, -3],
                         [-3, 0, 5],
                         [-3, 5, 5]], dtype=np.float32) / 15

    kernel_g8 = np.array([[5, 5, -3],
                         [5, 0, -3],
                         [-3, -3, -3]], dtype=np.float32) / 15
    g1 = cv2.filter2D(img, cv2.CV_64F, kernel_g1, anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g2 = cv2.filter2D(img, cv2.CV_64F, kernel_g2,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g3 = cv2.filter2D(img, cv2.CV_64F, kernel_g3,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g4 = cv2.filter2D(img, cv2.CV_64F, kernel_g4,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g5 = cv2.filter2D(img, cv2.CV_64F, kernel_g5,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g6 = cv2.filter2D(img, cv2.CV_64F, kernel_g6,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g7 = cv2.filter2D(img, cv2.CV_64F, kernel_g7,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    g8 = cv2.filter2D(img, cv2.CV_64F, kernel_g8,  anchor=(-1, -1), delta=0, borderType=cv2.BORDER_CONSTANT)
    magn = cv2.max(
        g1, cv2.max(
            g2, cv2.max(
                g3, cv2.max(
                    g4, cv2.max(
                        g5, cv2.max(
                            g6, cv2.max(
                                g7, g8
                            )
                        )
                    )
                )
            )
        )
    )
    return magn
