import numpy as np
from scipy import ndimage


def kirschEdges(imgIn):
    h1 = np.array([[5, -3, -3],
                   [5, 0, -3],
                   [5, -3, -3]])/15
    h2 = np.array([[-3, -3, 5],
                   [-3, 0, 5],
                   [-3, -3, 5]])/15
    h3 = np.array([[-3, -3, -3],
                   [5, 0, -3],
                   [5, 5, -3]])/15
    h4 = np.array([[-3, 5, 5],
                   [-3, 0, 5],
                   [-3, -3, -3]])/15
    h5 = np.array([[-3, -3, -3],
                   [-3, 0, -3],
                   [5, 5, 5]])/15
    h6 = np.array([[5, 5, 5],
                   [-3, 0, -3],
                   [-3, -3, -3]])/15
    h7 = np.array([[-3, -3, -3],
                   [-3, 0, 5],
                   [-3, 5, 5]])/15
    h8 = np.array([[5, 5, -3],
                   [5, 0, -3],
                   [-3, -3, -3]])/15

    t1 = ndimage.convolve(imgIn, h1)
    t2 = ndimage.convolve(imgIn, h2)
    t3 = ndimage.convolve(imgIn, h3)
    t4 = ndimage.convolve(imgIn, h4)
    t5 = ndimage.convolve(imgIn, h5)
    t6 = ndimage.convolve(imgIn, h6)
    t7 = ndimage.convolve(imgIn, h7)
    t8 = ndimage.convolve(imgIn, h8)

    imgOut = np.maximum(t1, t2)
    imgOut = np.maximum(imgOut, t3)
    imgOut = np.maximum(imgOut, t4)
    imgOut = np.maximum(imgOut, t5)
    imgOut = np.maximum(imgOut, t6)
    imgOut = np.maximum(imgOut, t7)
    imgOut = np.maximum(imgOut, t8)
    return imgOut
