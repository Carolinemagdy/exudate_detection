import re
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
import sys
from os import path
import os
from cv2 import resize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from utils import *
from misc.getFovMask import get_fov_mask
from misc.KirschEdges import kirsch_edges
import scipy
matplotlib.use('Qt5Agg')


ui, _ = loadUiType(path.join(path.dirname(__file__), 'image_viewer_ui.ui'))


class imageViewerApp(QMainWindow, ui):

    def __init__(self, parent=None):
        super(imageViewerApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_buttons()
        self.image_path = None

    def handle_buttons(self):
        """Initializing interface buttons"""
        self.browse_button.clicked.connect(self.browse)

    def show_message(self):
        """Show message for user"""
        message = QMessageBox()
        message.setWindowTitle("Error")
        message.setText("This file is corrupted !")
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Close | QMessageBox.Retry)
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
        '''Browse an image to extract its exudates'''
        #Getting file path
        self.image_path = QFileDialog.getOpenFileName(caption='Open image', filter = 'Images (*.jpg)',directory='.')

        self.browse_bar.setText(self.image_path[0])
        # check if an image was selected
        if self.image_path[0] == '':
            return

        #Clear View
        self.image_view.update()
        self.image_view_1.update()
        
        #Read Image
        img = cv2.imread(self.image_path[0],cv2.IMREAD_UNCHANGED)
        #Display Original Image
        _,axes = self.canvas_setup(550,600,self.image_view)
        axes.imshow(img)

        # Get nerve location
        onRow, onCol = self.get_on_loc()

        # Extract lesions
        imgProb = self.get_lesions(img, 1, onRow, onCol)

        # Display Extracted Exudates
        _, axes = self.canvas_setup(550, 600, self.image_view_1)
        axes.imshow(imgProb)

    def get_on_loc(self):
        """
        Get the location of the nerve from the meta file
        :return: the location of the nerve
        """
        onRow = [] 
        onCol = [] 
        metaFile = os.path.splitext(self.image_path[0])[0] + '.meta'
        print(metaFile)
        fMeta = open(metaFile, 'r')
        # if( fMeta > 0 ):
        res = fMeta.read()
        fMeta.close()
        tokRow = re.findall('ONrow\W+([0-9\.]+)', res)
        tokCol = re.findall('ONcol\W+([0-9\.]+)', res)
        if len(tokRow) > 0 and len(tokCol) > 0:
            onRow = int(tokRow[0])
            onCol = int(tokCol[0])
        return [onRow, onCol]
    
    @staticmethod
    @timeit
    def get_lesions(rgb_img_original,  remove_on,  on_y, on_x):
        """
        Extract the lesions from the image
        :param rgb_img_original: the original rgb image selected
        :param remove_on: whether to remove the nerve from the image
        :param on_y: the y coordinate of the nerve
        :param on_x: the x coordinate of the nerve
        :return: the image with the lesions extracted
        """
        win_on_ratio = [1 / 8, 1 / 8]

        original_size = rgb_img_original.shape

        new_size = np.array([750, round(750 * (original_size[1] / original_size[0]))])

        new_size = find_good_resolution_for_wavelet(new_size)

        new_size = new_size[::-1]

        img_rgb = resize(rgb_img_original, new_size, interpolation=cv2.INTER_AREA)

        img_g = img_rgb[:, :, 1]

        img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        imgV = img_hsv[:, :, 2]

        img_v8 = np.uint8(imgV)
        if remove_on:
            # get ON window
            on_y = np.round(on_y * new_size[0] / original_size[1])
            on_x = np.round(on_x * new_size[1] / original_size[0])

            win_on_size = np.round(win_on_ratio * new_size)
            # remove ON window from imgTh
            win_on_coord_y = [on_y - win_on_size[1],  on_y + win_on_size[1]]
            win_on_coord_x = [on_x - win_on_size[0], on_x + win_on_size[0]]

            if win_on_coord_y[0] < 0:
                win_on_coord_y[0] = 0
            if win_on_coord_x[0] < 0:
                win_on_coord_x[0] = 0
            if win_on_coord_y[1] > new_size[0]:
                win_on_coord_y[1] = new_size[0]
            if win_on_coord_x[1] > new_size[1]:
                win_on_coord_x[1] = new_size[1]

        win_on_coord_x = np.array(win_on_coord_x, dtype=np.int16)
        win_on_coord_y = np.array(win_on_coord_y, dtype=np.int16)

        img_fov_mask = get_fov_mask(img_v8, 30)
        img_fov_mask[win_on_coord_y[0]:win_on_coord_y[1], win_on_coord_x[0]:win_on_coord_x[1]] = 0
        img_fov_mask = img_fov_mask.astype(np.uint8)

        med_bg = get_median_filter(img_v8, new_size)

        img_th_no_od = get_subtracted_img(img_v8, med_bg, img_fov_mask)

        img_kirsch = kirsch_edges(img_g)

        img0 = img_g * np.uint8(img_th_no_od == 0)

        img0recon = reconstruction(img0, img_g)

        img0_kirsch = kirsch_edges(img0recon)

        img_edge_no_mask = img_kirsch - img0_kirsch
        imgEdge = img_fov_mask * img_edge_no_mask
        les_cand_img = np.zeros(new_size[::-1])
        les_cand = scipy.ndimage.measurements.label(img_th_no_od, structure=np.ones((3, 3)))[0]

        t1 = time.perf_counter()
        for idx_les in range(les_cand.max()):
            px_idx_list = les_cand == idx_les
            les_cand_img[px_idx_list] = np.sum(imgEdge[px_idx_list]) / px_idx_list.sum()

        t2 = time.perf_counter()
        les_cand_img = cv2.resize(les_cand_img, original_size[:2][::-1], interpolation=cv2.INTER_AREA)
        print('regionprops', t2 - t1)
        return les_cand_img

    @staticmethod
    @timeit
    def canvas_setup(fig_width, fig_height, view, flag=True):
        """Setting up a canvas to view an image in its graphics view"""
        scene = QGraphicsScene()
        figure = Figure(figsize=(fig_width / 90, fig_height / 90), dpi=90)
        canvas = FigureCanvas(figure)
        axes = figure.add_subplot()
        scene.addWidget(canvas)
        view.setScene(scene)
        if flag:
            figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
            axes.get_xaxis().set_visible(False)
            axes.get_yaxis().set_visible(False)
        else:
            axes.get_xaxis().set_visible(True)
            axes.get_yaxis().set_visible(True)
        return figure, axes
    
    @staticmethod
    def critical_message(window_title, message_sent):
        """Show error message for problem done by user"""
        message = QMessageBox()
        message.setWindowTitle(window_title)
        message.setText(message_sent)
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = imageViewerApp()
    window.show()
    app.exec_()
