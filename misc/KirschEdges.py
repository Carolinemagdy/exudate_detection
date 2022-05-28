import numpy as np
from scipy import ndimage
import cv2


def kirschEdges(gray):
    if gray.ndim > 2:
        raise Exception("Image should be grayscale.")
    kernelG1 = np.array([[5, 5, 5],
                         [-3, 0, -3],
                         [-3, -3, -3]], dtype=np.float32) / 15
    kernelG2 = np.array([[5, 5, -3],
                         [5, 0, -3],
                         [-3, -3, -3]], dtype=np.float32) / 15
    kernelG3 = np.array([[5, -3, -3],
                         [5, 0, -3],
                         [5, -3, -3]], dtype=np.float32) / 15
    kernelG4 = np.array([[-3, -3, -3],
                         [5, 0, -3],
                         [5, 5, -3]], dtype=np.float32) / 15
    kernelG5 = np.array([[-3, -3, -3],
                         [-3, 0, -3],
                         [5, 5, 5]], dtype=np.float32) / 15
    kernelG6 = np.array([[-3, -3, -3],
                         [-3, 0, 5],
                         [-3, 5, 5]], dtype=np.float32) / 15
    kernelG7 = np.array([[-3, -3, 5],
                         [-3, 0, 5],
                         [-3, -3, 5]], dtype=np.float32) / 15
    kernelG8 = np.array([[-3, 5, 5],
                         [-3, 0, 5],
                         [-3, -3, -3]], dtype=np.float32) / 15
    #g1 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG1), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    g1 = cv2.filter2D(gray, cv2.CV_64F, kernelG1)
    g2 = cv2.filter2D(gray, cv2.CV_64F, kernelG2)
    g3 = cv2.filter2D(gray, cv2.CV_64F, kernelG3)
    g4 = cv2.filter2D(gray, cv2.CV_64F, kernelG4)
    g5 = cv2.filter2D(gray, cv2.CV_64F, kernelG5)
    g6 = cv2.filter2D(gray, cv2.CV_64F, kernelG6)
    g7 = cv2.filter2D(gray, cv2.CV_64F, kernelG7)
    g8 = cv2.filter2D(gray, cv2.CV_64F, kernelG8)
    # g2 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG2), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g3 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG3), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g4 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG4), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g5 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG5), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g6 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG6), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g7 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG7), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    # g8 = cv2.normalize(cv2.filter2D(gray, cv2.CV_64F, kernelG8), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
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

