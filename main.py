import math
import re
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUiType
import sys
from os import path
import os
import cv2
from cv2 import resize
from cv2 import imshow
import numpy as np 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
from utils import *
from misc.getFovMask import getFovMask
from misc.KirschEdges import kirschEdges
import scipy

ui,_ = loadUiType(path.join(path.dirname(__file__),'image_viewer_ui.ui'))

class Image_Viewer_App(QMainWindow , ui):
    def __init__(self , parent=None):
        super(Image_Viewer_App , self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handle_Buttons()

    def Handle_Buttons(self):
        '''Initializing interface buttons'''
        self.browse_button.clicked.connect(self.Browse)   

    def show_message(self):
        message = QMessageBox()
        message.setWindowTitle("Error")
        message.setText("This file is corrupted !")
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Close|QMessageBox.Retry)
        message.setDefaultButton(QMessageBox.Retry)
        message.buttonClicked.connect(self.message_fn)
        self.image_info.clear()
        self.browse_bar.clear()
        self.image_info.setStyleSheet("background-color: rgb(251, 243, 255)")
        self.scene_1.clear()
        
        

    # message = QMessageBox()
    # message.setWindowTitle("Error")
    # message.setText("Generate image First !")
    # message.setIcon(QMessageBox.Critical)
    # message.setStandardButtons(QMessageBox.Close)
    # message.exec_()
    
    def Browse(self):
        '''Browse to get the image we want to interpolate'''
        #Getting file path
        self.image_path = QFileDialog.getOpenFileName(caption='Open image', filter = 'Images (*.jpg *.png)',directory='./DMED')
        self.browse_bar.setText(self.image_path[0])
        #check if an image was selected
        if self.image_path[0] == '':
            return

        #Read Image
        img = cv2.imread(self.image_path[0],cv2.IMREAD_UNCHANGED)

        #Display Original Image
        _,axes = self.canvas_setup(550,600,self.image_view)
        axes.imshow(img)

        #Get nerve location
        onRow, onCol = self.getONloc()

        #Extract lesions
        imgProb = self.getLesions(img, 1, onRow, onCol)

        # Display Extracted Exudates
        _,axes = self.canvas_setup(550,600,self.image_view_1)
        axes.imshow(imgProb)

    

    def getONloc(self ):
        onRow = [];
        onCol = [];
        metaFile = os.path.splitext(self.image_path[0])[0]+'.meta'
        print(metaFile)
        fMeta = open(metaFile, 'r');
        # if( fMeta > 0 ):
        res = fMeta.read()
        fMeta.close()
        tokRow = re.findall('ONrow\W+([0-9\.]+)',res)
        tokCol = re.findall('ONcol\W+([0-9\.]+)',res)
        if( len(tokRow)>0 and len(tokCol) >0):
            onRow = int(tokRow[0]);
            onCol = int(tokCol[0]);          
        return [onRow, onCol]
    
    def getLesions(self,rgbImgOrig, removeON, onY, onX):
        winOnRatio = [1/8, 1/8]

        origSize = rgbImgOrig.shape

        newSize = np.array([750, round(750*(origSize[1]/origSize[0]))])

        newSize = findGoodResolutionForWavelet(newSize)

        newSize = newSize[::-1]

        imgRGB = resize(rgbImgOrig, newSize, interpolation=cv2.INTER_AREA)

        imgG = imgRGB[:, :, 1]

        imgHSV = cv2.cvtColor(imgRGB, cv2.COLOR_RGB2HSV)

        imgV = imgHSV[:, :, 2]

        imgV8 = np.uint8(imgV)
        if removeON:
            # get ON window
            onY = np.round(onY * newSize[1]/origSize[1])
            onX = np.round(onX * newSize[0]/origSize[0])

            winOnSize = np.round(winOnRatio*newSize)
            # remove ON window from imgTh
            winOnCoordY = [onY-winOnSize[1], onY+winOnSize[1]]
            winOnCoordX = [onX-winOnSize[0], onX+winOnSize[0]]

            if winOnCoordY[0] < 0:
                winOnCoordY[0] = 0
            if winOnCoordX[0] < 0:
                winOnCoordX[0] = 0
            if winOnCoordY[1] > newSize[0]:
                winOnCoordY[1] = newSize[0]
            if winOnCoordX[1] > newSize[1]:
                winOnCoordX[1] = newSize[1]

        winOnCoordX = np.array(winOnCoordX, dtype=np.int16)
        winOnCoordY = np.array(winOnCoordY, dtype=np.int16)

        imgFovMask = getFovMask(imgV8, 1, 30)
        imgFovMask[winOnCoordY[0]:winOnCoordY[1], winOnCoordX[0]:winOnCoordX[1]] = 0
        imgFovMask = imgFovMask.astype(np.uint8)

        medBg = get_median_filt(imgV8, newSize)

        imgThNoOD = get_subtracted_img(imgV8, medBg, imgFovMask)

        imgKirsch = kirschEdges(imgG)

        img0 = imgG * np.uint8(imgThNoOD == 0)

        img0recon = reconstruction(img0, imgG)

        img0Kirsch = kirschEdges(img0recon)

        imgEdgeNoMask = imgKirsch - img0Kirsch

        imgEdge = imgFovMask * imgEdgeNoMask
        lesCandImg = np.zeros(newSize[::-1])


        lesCand = scipy.ndimage.measurements.label(imgThNoOD, structure=np.ones((3,3)))[0]
        for idxLes in range(lesCand.max()):
            pxIdxList = lesCand == idxLes
            lesCandImg[pxIdxList] = np.sum(imgEdge[pxIdxList]) / pxIdxList.sum()

        lesCandImg = cv2.resize(lesCandImg, origSize[:2][::-1], interpolation=cv2.INTER_AREA)
        return lesCandImg
    
    def canvas_setup(self,fig_width,fig_height,view,bool=True):
        '''Setting up a canvas to view an image in its graphics view'''
        scene= QGraphicsScene()
        figure = Figure(figsize=(fig_width/90, fig_height/90),dpi = 90)
        canvas = FigureCanvas(figure)
        axes = figure.add_subplot()
        scene.addWidget(canvas)
        view.setScene(scene)
        if bool ==True:
            figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
            axes.get_xaxis().set_visible(False)
            axes.get_yaxis().set_visible(False)
        else:
            axes.get_xaxis().set_visible(True)
            axes.get_yaxis().set_visible(True)
        return figure,axes
    
    def critical_message(self,window_title,messagee):
        '''Show error message for problem done by user'''
        message = QMessageBox()
        message.setWindowTitle(window_title)
        message.setText(messagee)
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Image_Viewer_App()
    window.show()
    app.exec_()
