
"""
@Name : CityGTV
"""
import matplotlib
matplotlib.use('Agg')

# import matplotlib.pyplot as plt
#
# # import xmlParser_Process as xp
# # import visualize_GML as vg
# from validation_Process import *
#
# import numpy as np
# from pyproj import Proj, transform, CRS
# import multiprocessing as mp
# from multiprocessing import Process, Manager, Queue, Pool
# import time
# import sys
# import random
# import os
# import shutil
# import xml.etree.ElementTree as ET
# from PyQt5.QtCore import Qt, QUrl, QCoreApplication, QPoint, pyqtSignal, QRectF, pyqtProperty, \
# QPropertyAnimation, QTimer, QThread, QStringListModel
# from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QMessageBox,\
# QLabel, QPushButton, QCheckBox, QFileDialog, QMainWindow, QHBoxLayout, QGroupBox, QGridLayout, \
# QStyleFactory, QComboBox, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QFrame, QProgressBar,\
# QCompleter, QListWidget, QAbstractItemView
# from PyQt5.QtGui import QPixmap, QFont, QDesktopServices, QBrush, QColor, QPalette, QIcon




# import of libraries
import os
import sys
import PySide2
from PySide2 import QtWidgets, QtGui
import CityGTV_gui_func as gtvgf
import transform_func as tf
# setting environment variable for PySide2
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path



# positions and dimensions of window
posx = 200
posy = 50
width = 650
height = 750
sizefactor = 0
sizer = True

pypath = os.path.dirname(os.path.realpath(__file__))        # path of script


class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(mainWindow,self).__init__()
        self.path_parent = os.path.dirname(os.getcwd())
        self.initUI()


    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer

        # setup of gui / layout
        if sizer:
            posx, posy, width, height, sizefactor = gtvgf.screenSizer(self, posx, posy, width, height, app)
            sizer = False
        gtvgf.windowSetup(self, posx, posy, width, height, pypath, 'CityGML Geometrical Transformation and Validation (CityGTV)')

        # Setting main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.Font_b = QtGui.QFont()
        self.Font_b.setBold(True)

        self.Font_i = QtGui.QFont()
        self.Font_i.setItalic(True)

        # Loading banner
        gtvgf.load_banner(self, os.path.join(pypath, r'pictures\CityGTV_header.png'), sizefactor)
        # self.lbl_descity = QtWidgets.QLabel(DESCity)
        # self.vbox.addWidget(self.lbl_descity)

        self.uGrid = QtWidgets.QGridLayout()

        self.btn_select_file = QtWidgets.QPushButton('Select CityGML file',
                                                     self)  # btn to select single .gml / .xml file or .zip folder
        self.uGrid.addWidget(self.btn_select_file, 0, 0, 1, 1)

        self.textbox_gml = QtWidgets.QLineEdit('')  # textbox to display single file path
        self.textbox_gml.setReadOnly(True)
        self.textbox_gml.setPlaceholderText('.gml path')
        self.uGrid.addWidget(self.textbox_gml, 0, 1, 1, 2)

        self.btn_select_folder = QtWidgets.QPushButton('Select folder for multiple files',
                                                       self)  # btn to select directory of .gml / .xml files
        self.uGrid.addWidget(self.btn_select_folder, 1, 0, 1, 1)

        self.textbox_gml_folder = QtWidgets.QLineEdit('')  # textbox to display directory path
        self.textbox_gml_folder.setReadOnly(True)
        self.textbox_gml_folder.setPlaceholderText('directory path')
        self.uGrid.addWidget(self.textbox_gml_folder, 1, 1, 1, 2)

        self.btn_select_output = QtWidgets.QPushButton('Select output folder',
                                                       self)  # btn to select directory of .gml / .xml files
        self.uGrid.addWidget(self.btn_select_output, 2, 0, 1, 1)

        self.textbox_gml_output = QtWidgets.QLineEdit('')  # textbox to display directory path
        self.textbox_gml_output.setReadOnly(True)
        self.textbox_gml_output.setPlaceholderText('directory path')
        self.uGrid.addWidget(self.textbox_gml_output, 2, 1, 1, 2)

        self.tbl_buildings = QtWidgets.QTableWidget()
        self.tbl_buildings.setColumnCount(3)
        self.tbl_buildings.setHorizontalHeaderLabels(['File Name', 'Name of Building', 'Level of Detail (LoD)'])
        self.tbl_buildings.verticalHeader().hide()
        # self.tbl_buildings.horizontalHeader().hide()
        self.tbl_buildings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_buildings.setEnabled(False)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tbl_buildings.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.uGrid.addWidget(self.tbl_buildings, 3, 0, 9, 3)

        self.vbox.addLayout(self.uGrid)

        self.lGrid = QtWidgets.QGridLayout()

        self.btn_transformation = QtWidgets.QPushButton('Transformation', self)  # btn to reset window to defaults
        self.lGrid.addWidget(self.btn_transformation, 0, 0, 1, 1)

        self.btn_validation = QtWidgets.QPushButton('Validation', self)  # btn to jump to 'validation' window
        self.lGrid.addWidget(self.btn_validation, 0, 1, 1, 1)

        # self.btn_crop = QtWidgets.QPushButton('Crop Dataset', self)  # btn to jump to 'save' window
        # self.lGrid.addWidget(self.btn_crop, 0, 3, 1, 3)

        self.btn_visualize = QtWidgets.QPushButton('Visualize', self)  # btn to jump to 'search' window
        self.lGrid.addWidget(self.btn_visualize, 0, 2, 1, 1)

        self.btn_about = QtWidgets.QPushButton('About', self)  # btn to jump to 'about' window
        self.lGrid.addWidget(self.btn_about, 1, 0, 1, 1)

        # self.btn_reset = QtWidgets.QPushButton('Reset', self)  # btn to close programme
        # self.lGrid.addWidget(self.btn_reset, 2, 3, 1, 3)

        self.btn_mainWindow = QtWidgets.QPushButton('Main Window', self)  # btn to close programme
        self.lGrid.addWidget(self.btn_mainWindow, 1, 1, 1, 1)

        self.btn_exit = QtWidgets.QPushButton('Exit', self)  # btn to jump to 'about' window
        self.lGrid.addWidget(self.btn_exit, 1, 2, 1, 1)

        self.vbox.addLayout(self.lGrid)

        # binding buttons to functions
        self.btn_select_file.clicked.connect(self.func_select_file)
        self.btn_select_folder.clicked.connect(self.func_select_folder)
        # self.btn_reset.clicked.connect(self.func_new_search)
        self.btn_transformation.clicked.connect(self.open_transformation)
        self.btn_visualize.clicked.connect(self.open_visual)

    def func_select_file(self):
            global gmlpath, dirpath
            gmlpath, dirpath = gtvgf.select_gml(self)

    def func_select_folder(self):
            global dirpath
            dirpath = gtvgf.select_folder(self)

    def func_new_search(self):
        global gmlpath, dirpath, data
        gtvgf.new_search(self)
        gmlpath = ''
        dirpath = ''
        data = []

    def open_transformation(self):
        global posx, posy
        posx, posy = gtvgf.dimensions(self)
        gtvgf.next_window(self, transformation())


    def open_visual(self):
        global posx, posy
        posx, posy = gtvgf.dimensions(self)
        gtvgf.next_window(self, static_visual())

    # def open_transformation(self):
    #     global posx, posy
    #     posx, posy = gtvgf.dimensions(self)
    #     gtvgf.next_window(self, transformation())
    #
    # def open_transformation(self):
    #     global posx, posy
    #     posx, posy = gtvgf.dimensions(self)
    #     gtvgf.next_window(self, transformation())
    #
    # def open_transformation(self):
    #     global posx, posy
    #     posx, posy = gtvgf.dimensions(self)
    #     gtvgf.next_window(self, transformation())


class transformation(QtWidgets.QWidget):
    def __init__(self):
        # initiate the parent
        super(transformation, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        gtvgf.windowSetup(self, posx, posy, width, height, pypath, 'CityGTV - Transform CityGML Models')

        # setup of gui / layout
        self.vbox_transform = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox_transform)

        coordinateReferenceSystems = ['', 'EPSG:2056', 'EPSG:2263', 'EPSG:25830', 'EPSG:25832', 'EPSG:25833', 'EPSG:27700', 'EPSG:28992', 'EPSG:2979', 'EPSG:31256', 'EPSG:31370', 'EPSG:31467', 'EPSG:32118', 'EPSG:32626', 'EPSG:32627', 'EPSG:32628', 'EPSG:3879', 'EPSG:4326', 'EPSG:4979']


        self.groupbox = QtWidgets.QGroupBox(' Coordinate Selection ')
        self.vbox_transform.addWidget(self.groupbox)
        self.groupbox.setStyleSheet(
            "QGroupBox {border: 1px solid rgb(90,90,90);margin-top: 20px;} QGroupBox::title {bottom: 6px; left: 5px;}")

        self.mGrid = QtWidgets.QGridLayout()
        self.groupbox.setLayout(self.mGrid)

        self.lbl_iCRS = QtWidgets.QLabel('Input CRS:')
        self.mGrid.addWidget(self.lbl_iCRS, 0, 0, 1, 1)

        self.combobox_input = QtWidgets.QComboBox()
        self.combobox_input.addItems(coordinateReferenceSystems)
        self.mGrid.addWidget(self.combobox_input, 0, 1, 1, 2)

        self.lbl_oCRS = QtWidgets.QLabel('Output CRS:')
        self.mGrid.addWidget(self.lbl_oCRS, 0, 4, 1, 1)

        self.combobox_output = QtWidgets.QComboBox()
        self.combobox_output.addItems(coordinateReferenceSystems)
        self.mGrid.addWidget(self.combobox_output, 0, 5, 1, 2)

        self.lbl_x = QtWidgets.QLabel('Longitude:')
        self.mGrid.addWidget(self.lbl_x, 2, 0, 1, 1)

        self.QL_x = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.QL_x, 2, 1, 1, 2)
        self.QL_x.setPlaceholderText('enter longitude')

        self.lbl_y = QtWidgets.QLabel('Latitude:')
        self.mGrid.addWidget(self.lbl_y, 2, 4, 1, 1)

        self.QL_y = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.QL_y, 2, 5, 1, 2)
        self.QL_y.setPlaceholderText('enter latitude')

        self.btn_addpoint = QtWidgets.QPushButton('Add Point', self)
        self.mGrid.addWidget(self.btn_addpoint, 3, 5, 1, 2)

        self.lbl_x_user = QtWidgets.QLabel('X coordinate:')
        self.mGrid.addWidget(self.lbl_x_user, 5, 0, 1, 1)

        self.x_user = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.x_user, 5, 1, 1, 2)
        self.x_user.setPlaceholderText('X coordinate entered')
        self.x_user.setEnabled(False)

        self.lbl_y_user = QtWidgets.QLabel('Y coordinate:')
        self.mGrid.addWidget(self.lbl_y_user, 5, 4, 1, 1)

        self.y_user = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.y_user, 5, 5, 1, 2)
        self.y_user.setPlaceholderText('Y coordinate entered')
        self.y_user.setEnabled(False)


        self.btn_delpoint = QtWidgets.QPushButton('Delete', self)
        self.mGrid.addWidget(self.btn_delpoint, 6, 5, 1, 2)


        self.groupbox_rotation = QtWidgets.QGroupBox('Rotation and Elevation')
        self.vbox_transform.addWidget(self.groupbox_rotation)
        self.groupbox_rotation.setStyleSheet(
            "QGroupBox {border: 1px solid rgb(90,90,90);margin-top: 20px;} QGroupBox::title {bottom: 6px; left: 5px;}")

        self.lGrid = QtWidgets.QGridLayout()
        self.groupbox_rotation.setLayout(self.lGrid)

        self.lbl_rotation = QtWidgets.QLabel('Enter rotation angle [-360,360]: ')
        self.lGrid.addWidget(self.lbl_rotation, 0, 0, 1, 1)

        self.line_rotation = QtWidgets.QLineEdit('')
        self.lGrid.addWidget(self.line_rotation, 0, 1, 1, 1)
        self.line_rotation.setPlaceholderText('0')

        self.btn_rotation = QtWidgets.QPushButton('Transformation')
        self.lGrid.addWidget(self.btn_rotation, 0, 2, 1, 1)

        self.lbl_elevation = QtWidgets.QLabel('Enter elevation [m]: ')
        self.lGrid.addWidget(self.lbl_elevation, 1, 0, 1, 1)

        self.line_elevation = QtWidgets.QLineEdit('')
        self.lGrid.addWidget(self.line_elevation, 1, 1, 1, 1)
        self.line_elevation.setPlaceholderText('0')

        self.btn_elevation = QtWidgets.QPushButton('Elevation')
        self.lGrid.addWidget(self.btn_elevation, 1, 2, 1, 1)

        self.tlGrid = QtWidgets.QGridLayout()

        self.btn_transform_select = QtWidgets.QPushButton('Transform')
        self.tlGrid.addWidget(self.btn_transform_select, 0, 0, 1, 1)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.tlGrid.addWidget(self.progress_bar, 0, 1, 1, 2)

        self.btn_back = QtWidgets.QPushButton('Back')
        self.tlGrid.addWidget(self.btn_back, 1, 0, 1, 1)

        self.btn_exit_gtv = QtWidgets.QPushButton('Exit CityGTV')
        self.tlGrid.addWidget(self.btn_exit_gtv, 1, 1, 1, 1)

        self.btn_exit_des = QtWidgets.QPushButton('Exit DESCity')
        self.tlGrid.addWidget(self.btn_exit_des, 1, 2, 1, 1)

        self.vbox_transform.addLayout(self.tlGrid)

        self.btn_addpoint.clicked.connect(self.add_lat)
        self.btn_delpoint.clicked.connect(self.delete_point)
        self.btn_transform_select.clicked.connect(self.transform_models)
        self.btn_back.clicked.connect(self.back_clicked)

        self.btn_exit_des.clicked.connect(self.func_exit)

    def add_lat(self):
        tf.transformLonLat(self)

    def delete_point(self):
        tf.delpoint(self)

    def transform_models(self):
        tf.transformmodels(self)

    def func_exit(self):
        gtvgf.close_application(self)

    def back_clicked(self):
        # def main_winodw(self):
        global posx, posy
        posx, posy = gtvgf.dimensions(self)
        gtvgf.next_window(self, mainWindow())


class static_visual(QtWidgets.QWidget):
    def __init__(self):
        # initiate the parent
        super(static_visual, self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        gtvgf.windowSetup(self, posx, posy, width, height, pypath, 'CityGTV - Static Visualization CityGML Models')

        # setup of gui / layout
        self.vbox_visual = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox_visual)

        self.groupbox_visual = QtWidgets.QGroupBox()
        self.vbox_visual.addWidget(self.groupbox_visual)
        self.groupbox_visual.setStyleSheet(
            "QGroupBox {border: 1px solid rgb(90,90,90);margin-top: 20px;} QGroupBox::title {bottom: 6px; left: 5px;}")

        self.mGrid = QtWidgets.QGridLayout()
        self.groupbox_visual.setLayout(self.mGrid)

        self.box_input = QtWidgets.QGroupBox('Input GML Models')
        self.mGrid.addWidget(self.box_input, 0, 0, 1, 1)

        self.vboxgrid_inputvisual = QtWidgets.QGridLayout()
        self.box_input.setLayout(self.vboxgrid_inputvisual)

        self.lbl_igml_picture = QtWidgets.QLabel()
        self.vboxgrid_inputvisual.addWidget(self.lbl_igml_picture, 0, 0, 3, 3)

        self.saveas_inp = QtWidgets.QPushButton('Save As')
        self.vboxgrid_inputvisual.addWidget(self.saveas_inp, 4, 3, 1, 1)


        self.box_output = QtWidgets.QGroupBox('Output GML Models')
        self.mGrid.addWidget(self.box_output, 1, 0, 1, 1)

        self.vboxgrid_outputvisual = QtWidgets.QGridLayout()
        self.box_output.setLayout(self.vboxgrid_outputvisual)

        self.lbl_ogml_picture = QtWidgets.QLabel()
        self.vboxgrid_outputvisual.addWidget(self.lbl_ogml_picture, 0, 0, 3, 3)

        self.saveas_out = QtWidgets.QPushButton('Save As')
        self.vboxgrid_outputvisual.addWidget(self.saveas_out, 4, 3, 1, 1)

        # self.lbl_igml = QtWidgets.QLabel('Input GML Models')
        # self.mGrid.addWidget(self.lbl_igml, 0, 1, 1, 2)

        # self.lbl_igml_picture = QtWidgets.QLabel()
        # self.mGrid.addWidget(self.lbl_igml_picture, 1, 0, 3, 2)

        # self.saveas_inp = QtWidgets.QPushButton('Save As')
        # self.mGrid.addWidget(self.saveas_inp, 2, 1, 1, 1)

        # self.lbl_ogml = QtWidgets.QLabel('Output GML Models')
        # self.mGrid.addWidget(self.lbl_ogml, 0, 3, 1, 2)

        # self.lbl_ogml_picture = QtWidgets.QLabel()
        # self.mGrid.addWidget(self.lbl_ogml_picture, 1, 3, 3, 2)
        #
        # self.saveas_out = QtWidgets.QPushButton('Save As')
        # self.mGrid.addWidget(self.saveas_out,2, 3, 1, 1)


        self.lGrid = QtWidgets.QGridLayout()

        self.btn_back = QtWidgets.QPushButton('Back')
        self.lGrid.addWidget(self.btn_back, 0, 0, 1, 1)

        self.btn_exit_gtv = QtWidgets.QPushButton('Exit CityGTV')
        self.lGrid.addWidget(self.btn_exit_gtv, 0, 1, 1, 1)

        self.btn_exit_des = QtWidgets.QPushButton('Exit DESCity')
        self.lGrid.addWidget(self.btn_exit_des, 0, 2, 1, 1)

        self.vbox_visual.addLayout(self.lGrid)

        self.btn_back.clicked.connect(self.back_clicked)
        self.btn_exit_des.clicked.connect(self.func_exit)

    def func_exit(self):
        gtvgf.close_application(self)

    def back_clicked(self):
        # def main_winodw(self):
        global posx, posy
        posx, posy = gtvgf.dimensions(self)
        gtvgf.next_window(self, mainWindow())


# from win32api import GetSystemMetrics
#
# if hasattr(Qt, 'AA_EnableHighDpiScaling'):
#     QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
#
# if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
#     QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
#
# # Check https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtwidgets/qtwidgets-module.html
# # for more components from QtWidgets
#
#
# #--------------------------------------------------
# # using Thread to avoid freezing the UI while processing some heavy work.
# # Thread for transformation via multiprocessing
# class WorkerThread(QThread):
#     finished = pyqtSignal(float)
#     def __init__(self, parent=None):
#         super(WorkerThread, self).__init__(parent)
#
#         self.buildingList = []
#
#         self.manager = Manager()
#         self.buildingResult = self.manager.list()
#
#         self.OFFSET = np.array([0,0,0])
#         self.inputCRS = ""
#         self.outputCRS = ""
#         self.angle = 0
#         self.elevationChange = 0
#         self.fileName_input = ""
#         self.fileName_exported = ""
#         self.selectionReference = []
#         self._nameSpace = {"key":"value"}
#
#     def run(self):
#         #self.do_work()
#         start_time = time.time()
#
#         inProj = Proj(self.inputCRS)
#         outProj = Proj(self.outputCRS)
#
#         pool = Pool()
#         pool.starmap(crsTransformPool,\
#             [(self.buildingList,self.buildingResult,loc,self.OFFSET,inProj,outProj,\
#                 self.angle,self.elevationChange,self.selectionReference) \
#            for loc in range(len(self.buildingList))])
#
#         pool.close()
#         pool.join()
#
#         # Update buildingList with the buildingResult, which contains the transformation results.
#         print("number of results",len(self.buildingResult))
#         print("cpu_count = ",mp.cpu_count())
#         print("Transformation completed successfully.")
#
#         # export the List to an XML
#         treeWriter(self.fileName_exported,ET.parse(self.fileName_input),\
#             self.buildingResult,self._nameSpace)
#
#         self.finished.emit(float(time.time()-start_time))
#
# #Thread for drawing.
# class DrawingThread(QThread):
#     finished = pyqtSignal(bool)
#     def __init__(self, parent=None):
#         super(DrawingThread, self).__init__(parent)
#         self.fileName_xml = ""
#         self.fileName_png = ""
#         self.myDPI = 600
#         self.isInput = True
#
#     def run(self):
#         print("Export .png file to the working directory:\n"+self.fileName_png)
#         drawXML(self.fileName_xml, self.fileName_png, self.myDPI)
#         self.finished.emit(self.isInput)
#
# class ValidationThread(QThread):
#     finished = pyqtSignal(list)
#     def __init__(self, parent=None):
#         super(ValidationThread, self).__init__(parent)
#         self.buildingList = []
#         self.manager = Manager()
#         self.buildingResult = self.manager.list()
#         self.isInput = True
#
#     def run(self):
#         #self.do_work()
#         start_time = time.time()
#
#         pool = Pool()
#         pool.starmap(validation,\
#             [(self.buildingList,self.buildingResult,loc) for loc in range(len(self.buildingList))])
#
#         pool.close()
#         pool.join()
#
#         # Update buildingList with the buildingResult, which contains the transformation results.
#         print("number of results",len(self.buildingResult))
#         print("cpu_count = ",mp.cpu_count())
#
#         self.finished.emit([time.time() - start_time, self.isInput])
#
# # Button that can be flashing in colors.
# class BlinkButton(QPushButton):
#     def __init__(self, *args, **kwargs):
#         QPushButton.__init__(self, *args, **kwargs)
#         self.default_color = QColor(0,0,0)
#
#     def getColor(self):
#         return self.palette().color(QPalette.Button)
#
#     def setColor(self, value):
#         self.setStyleSheet("background-color: rgb(238, 248, 255)")
#         if value == self.getColor():
#             return
#         palette = self.palette()
#         palette.setColor(self.foregroundRole(), value)
#         self.setAutoFillBackground(True)
#         self.setPalette(palette)
#
#     def reset_color(self):
#         self.setColor(self.default_color)
#         self.setStyleSheet("background-color: rgb(238, 248, 255);")
#
#     color = pyqtProperty(QColor, getColor, setColor)
#
# # Build a class for our main window. All stuffs will be displayed at this main window.
# # This class Window inherits from PyQt5.QtWidgets.QDialog
# class _MainWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_MainWindow, self).__init__(parent)
#
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle('Main Window')
#
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         #------------------------------------------------------------------------
#         # sign to indicate whether transformed
#         self.isTransformed = False
#
#         # determine screen resolution
#         try:
#             self.screenWidth = GetSystemMetrics(0)
#             self.screenHeight =  GetSystemMetrics(1)
#         except:
#             self.screenWidth = 500
#             self.screenHeight = 400
#
#         if self.screenWidth <= 2400 or self.screenHeight <= 1200:
#             self.w = 500
#             self.h = 400
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k or higher high-resolution
#             self.w = 500
#             self.h = 400
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         self.resize(self.w,self.h)
#         self.theme = "Light"
#         #Default Theme
#         self.setStyleSheet("background-color:rgb(255, 250, 240);")
#         #------------------------------------------------------------------------
#
#         # set the base layout
#         self.vbox = QVBoxLayout()
#         self.setLayout(self.vbox)
#         self.vbox.setDirection(2) #QBoxLayout::TopToBottom
#         #------------------------------------------------------------------------
#         self.lbl_cover = QLabel()
#         # self.pixmap_cover = QPixmap("e3dHeaderGTV.png")
#         # self.pixmap_cover = self.pixmap_cover.scaled(self.w,int(self.w/4))
#         # self.lbl_cover.setPixmap(self.pixmap_cover)
#         self.lbl_cover.setPixmap(QPixmap("e3dHeaderGTV.png"))
#         self.lbl_cover.setScaledContents(True)
#         self.lbl_cover.setMinimumHeight(self.h/3)
#         self.lbl_cover.setMaximumHeight(self.h/3)
#         self.lbl_cover.setMinimumWidth(700)
#         self.lbl_cover.setMaximumWidth(700)
#         self.vbox.addWidget(self.lbl_cover)
#
#         #Theme selection
#         self.hbox_theme = QHBoxLayout()
#         self.hbox_theme.setAlignment(Qt.AlignLeft)
#         self.vbox.addLayout(self.hbox_theme)
#         self.lbl_theme = QLabel("Theme Preference:     ")
#         self.lbl_theme.setFont(self.myBoldFont)
#         #dark blue
#         #self.lbl_theme.setStyleSheet("color:rgb(35, 46, 130)")
#         #dark grey
#         self.lbl_theme.setStyleSheet("color:rgb(39, 39, 39)")
#         self.hbox_theme.addWidget(self.lbl_theme)
#
#
#         self.cmb_theme = QComboBox()
#         self.cmb_theme.addItems(['Light        ','Dark        ']) #with 8 spaces
#         self.cmb_theme.setFont(self.myBoldFont)
#         #dark blue
#         #self.cmb_theme.setStyleSheet("color:rgb(35, 46, 130)")
#         #dark grey
#         self.cmb_theme.setStyleSheet("color:rgb(39, 39, 39)")
#         self.cmb_theme.currentIndexChanged.connect(self.changeTheme)
#         self.hbox_theme.addWidget(self.cmb_theme)
#
#         # About this app/tool
#         self.btn_about_this_app = QPushButton("About This Tool")
#         self.btn_about_this_app.clicked.connect(self.aboutThisTool)
#         self.btn_about_this_app.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_about_this_app.setFont(self.myBoldFont)
#         self.hbox_theme.addStretch(2)
#         self.hbox_theme.addWidget(self.btn_about_this_app)
#
#         # Label, from QTWidgets, a fake title
#         self.lbl_title = QLabel("InputGML File Information:  Please select input xml/gml file.")
#         self.lbl_title.setFont(self.myBoldFont)
#         #dark blue
#         #self.lbl_title.setStyleSheet("color:rgb(35, 46, 130)")
#         #dark grey
#         self.lbl_title.setStyleSheet("color:rgb(39, 39, 39)")
#         # After widget creation, it has to be added to the LAYOUT.
#         self.vbox.addWidget(self.lbl_title)
#
#         #------------------------------------------------------------------------
#
#         # Module: file settings
#         self.gbox_fileSettings = QGroupBox("")
#         self.vbox_fileSettings = QVBoxLayout()
#         self.gbox_fileSettings.setLayout(self.vbox_fileSettings)
#         self.vbox.addWidget(self.gbox_fileSettings)
#
#         self.filename_input = ""
#         self.filename_output = ""
#
#         #self.btn_input_xml = QPushButton("Input XML/GML File")
#         self.btn_input_xml = BlinkButton("Input XML/GML File")
#         self.btn_input_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255)}""")
#         self.btn_input_xml.setFont(self.myBoldFont)
#         self.btn_input_xml.clicked.connect(self.input_xml)
#
#         self.animation = QPropertyAnimation(self.btn_input_xml, b"color", self)
#
#         self.animButton(self.btn_input_xml)
#
#         self.hbox_folder = QHBoxLayout()
#
#         self.btn_select_folder = BlinkButton("Select Folder")
#         self.btn_select_folder.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255);}""")
#         self.btn_select_folder.setFont(self.myBoldFont)
#         self.btn_select_folder.clicked.connect(self.selectFolder)
#         self.hbox_folder.addWidget(self.btn_select_folder)
#         # disabled at beginning
#         self.btn_select_folder.setEnabled(False)
#
#
#         self.btn_create_folder = BlinkButton("New Folder")
#         self.btn_create_folder.setStyleSheet(
#                 """QPushButton { background-color: rgb(180, 180, 180);}""")
#         self.btn_create_folder.setFont(self.myBoldFont)
#         self.btn_create_folder.clicked.connect(self.openFolderWindow)
#         self.hbox_folder.addWidget(self.btn_create_folder)
#         self.btn_create_folder.setEnabled(False)
#
#         self.edit_select_folder= QLineEdit("Please Select Saving Folder")
#         self.edit_select_folder.setStyleSheet(
#                 """QLineEdit { background-color: rgb(180, 190, 210); color: black }""")
#         self.edit_select_folder.setFont(self.mySlimFont)
#         self.edit_select_folder.setReadOnly(True)
#
#         self.vbox_fileName = QVBoxLayout()
#         self.edit_input_xml = QLineEdit("Please Select GML File")
#         self.edit_input_xml.setStyleSheet(
#                 """QLineEdit { background-color: rgb(180, 190, 210); color: black }""")
#         self.edit_input_xml.setFont(self.mySlimFont)
#         self.edit_input_xml.setReadOnly(True)
#
#         self.edit_output_xml = QLineEdit("testing5.xml")
#         self.edit_output_xml.setStyleSheet(
#                 """QLineEdit { background-color: rgb(180, 190, 210); color: black }""")
#         self.edit_output_xml.setFont(self.mySlimFont)
#         self.edit_output_xml.setReadOnly(True)
#
#         self.vbox_fileSettings.addWidget(self.btn_input_xml)
#         self.vbox_fileSettings.addWidget(self.edit_input_xml)
#         self.vbox_fileSettings.addLayout(self.hbox_folder)
#         self.vbox_fileSettings.addWidget(self.edit_select_folder)
#
#         #------------------------------------------------------------------------
#
#         # Transform xml
#         self.btn_transform_xml = BlinkButton("Transformation")
#         self.btn_transform_xml.clicked.connect(self.openTransformationWindow)
#         self.btn_transform_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255);}""")
#         self.btn_transform_xml.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.btn_transform_xml)
#         #------------------------------------------------------------------------
#
#         # Draw Figures
#         self.btn_draw_xml = BlinkButton("Visualization")
#         self.btn_draw_xml.clicked.connect(self.openDrawWindow)
#         self.btn_draw_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255);}""")
#         self.btn_draw_xml.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.btn_draw_xml)
#         #------------------------------------------------------------------------
#
#         # Validate XMLs
#         self.btn_validate_xml = BlinkButton("Validation")
#         self.btn_validate_xml.clicked.connect(self.openValidationWindow)
#         self.btn_validate_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255);}""")
#         self.btn_validate_xml.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.btn_validate_xml)
#         #------------------------------------------------------------------------
#
#         # Crop buildings, e.g. get a file of 50 building out of an Input CityGML with 1153 buildings.
#         # Select the first X buildings. Take whatever X you want, as long as X is less than the number of buildings
#         # in the Input file.
#         self.btn_crop_xml = QPushButton("Crop Buildings")
#         self.btn_crop_xml.clicked.connect(self.openCropWindow)
#         self.btn_crop_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_crop_xml.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.btn_crop_xml)
#         #------------------------------------------------------------------------
#
#         # Exit
#         self.btn_close_application = QPushButton('Exit',self)
#         self.vbox.addWidget(self.btn_close_application)
#         self.btn_close_application.clicked.connect(self.close_application)
#         self.btn_close_application.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_close_application.setFont(self.myBoldFont)
#
#
#         # for parsing XML files.
#         # nameSpace used for ElementTree's search function
#         self._nameSpace1 = {'core':"http://www.opengis.net/citygml/1.0",
#         'gen':"http://www.opengis.net/citygml/generics/1.0",
#         'grp':"http://www.opengis.net/citygml/cityobjectgroup/1.0",
#         'app':"http://www.opengis.net/citygml/appearance/1.0",
#         'bldg':"http://www.opengis.net/citygml/building/1.0",
#         'gml':"http://www.opengis.net/gml",
#         'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
#         'xlink':"http://www.w3.org/1999/xlink",
#         'xsi':"http://www.w3.org/2001/XMLSchema-instance"}
#
#         # CityGML 2.0
#         self._nameSpace2 = {'core':"http://www.opengis.net/citygml/2.0",
#         'gen':"http://www.opengis.net/citygml/generics/2.0",
#         'grp':"http://www.opengis.net/citygml/cityobjectgroup/2.0",
#         'app':"http://www.opengis.net/citygml/appearance/2.0",
#         'bldg':"http://www.opengis.net/citygml/building/2.0",
#         'gml':"http://www.opengis.net/gml",
#         'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
#         'xlink':"http://www.w3.org/1999/xlink",
#         'xsi':"http://www.w3.org/2001/XMLSchema-instance"}
#
#         self.version = 0
#
#
#         #disable buttons
#         self.btn_transform_xml.setEnabled(False)
#         self.btn_transform_xml.setStyleSheet("background-color: rgb(180, 180, 180); color: black")
#         self.btn_draw_xml.setEnabled(False)
#         self.btn_draw_xml.setStyleSheet("background-color: rgb(180, 180, 180); color: black")
#         self.btn_validate_xml.setEnabled(False)
#         self.btn_validate_xml.setStyleSheet("background-color: rgb(180, 180, 180); color: black")
#
#         # msgBox
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#
#     def changeTheme(self):
#         if self.cmb_theme.currentText()[0:5] == 'Light':
#             self.theme = "Light"
#             print("theme = ",self.cmb_theme.currentText()[0:5])
#             self.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240)}""")
#             '''
#             #dark blue
#             self.lbl_theme.setStyleSheet("color:rgb(35, 46, 130)")
#             self.lbl_title.setStyleSheet("color:rgb(35, 46, 130)")
#             self.cmb_theme.setStyleSheet("""QComboBox{color: rgb(35, 46, 130);
#                                         background-color: rgb(255, 250, 240)}""")
#             '''
#             #dark grey
#             self.lbl_theme.setStyleSheet("color:rgb(39, 39, 39)")
#             self.lbl_title.setStyleSheet("color:rgb(39, 39, 39)")
#             self.cmb_theme.setStyleSheet("""QComboBox{color: rgb(39, 39, 39);
#                                         background-color: rgb(255, 250, 240)}""")
#         else:
#             self.theme = "Dark"
#             print("theme = ",self.theme)
#             self.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30)}""")
#             self.lbl_theme.setStyleSheet("color:rgb(238, 248, 255)")
#             self.lbl_title.setStyleSheet("color:rgb(238, 248, 255)")
#             self.cmb_theme.setStyleSheet("""QComboBox{color: rgb(238, 248, 255);
#                                         background-color: rgb(20, 25, 30)}""")
#
#     def animButton(self,button):
#         # create one animation for each button in the buttonList
#         self.animation = QPropertyAnimation(button, b"color", self)
#         self.animation.setDuration(1000)
#         self.animation.setLoopCount(100)
#
#         self.animation.setStartValue(button.default_color)
#         self.animation.setEndValue(button.default_color)
#
#         self.animation.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animation.start()
#
#     def animVisualization(self):
#         # create one animation for each button in the buttonList
#         self.animationVis = QPropertyAnimation(self.btn_draw_xml, b"color", self)
#         self.animationVis.setDuration(1000)
#         self.animationVis.setLoopCount(100)
#         self.animationVis.setStartValue(self.btn_draw_xml.default_color)
#         self.animationVis.setEndValue(self.btn_draw_xml.default_color)
#         self.animationVis.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animationVis.start()
#
#     def animValidation(self):
#         # create one animation for each button in the buttonList
#         self.animationVal = QPropertyAnimation(self.btn_validate_xml, b"color", self)
#         self.animationVal.setDuration(1000)
#         self.animationVal.setLoopCount(100)
#         self.animationVal.setStartValue(self.btn_validate_xml.default_color)
#         self.animationVal.setEndValue(self.btn_validate_xml.default_color)
#         self.animationVal.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animationVal.start()
#
#     def selectFolder(self):
#         self.workingDirectory = str(QFileDialog.getExistingDirectory(self,"Select Working Directory"))
#         if self.workingDirectory:
#             self.edit_select_folder.setText(self.workingDirectory)
#             self.btn_create_folder.setEnabled(True)
#             self.btn_create_folder.setStyleSheet("background-color: rgb(238, 248, 255);")
#
#
#             self.animation.stop()
#             self.btn_select_folder.reset_color()
#             self.animButton(self.btn_create_folder)
#
#         else:
#             self.edit_select_folder.setText('No Folder Selected')
#
#     def input_xml(self):
#         self.filename_input = QFileDialog.getOpenFileName(self, 'Select Input GML')[0]
#         print("InputGML=",self.filename_input)
#
#         if self.filename_input:
#             self.edit_input_xml.setText(self.filename_input)
#             try:
#                 # determine _nameSpace for XML parser
#                 with open(self.filename_input,"r") as fileHandle:
#                     for line in fileHandle.readlines():
#                         #print("current line = ",line)
#                         if str(line).find("citygml/1.0")!= -1:
#                             self._nameSpace = self._nameSpace1
#                             self.version = 1
#                             print("CityGml Version = 1.0")
#                             break
#                         elif str(line).find("citygml/2.0")!= -1:
#                             self._nameSpace = self._nameSpace2
#                             self.version = 2
#                             print("CityGML Version = 2.0")
#                             break
#                     # end loop
#                     if self.version == 0:
#                         print("CityGML Version Not Supported.")
#                         return -1
#                 #file closed
#
#                 buildingList = readCityGML(self.filename_input,self._nameSpace)
#                 tmp_text = 'InputGML File Information:  CityGML Version = '+str(self.version)+\
#                 '.0    Number of buildings = '+str(len(buildingList))
#                 self.lbl_title.setText(tmp_text)
#
#                 self.animation.stop()
#                 self.btn_input_xml.reset_color()
#                 self.animButton(self.btn_select_folder)
#                 self.btn_select_folder.setEnabled(True)
#             except:
#                 if self.theme == "Light":
#                     '''
#                     #dark blue
#                     self.msg.setStyleSheet("""QLabel{color:rgb(35, 46, 130)}
#                             QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#                     '''
#                     #dark grey
#                     self.msg.setStyleSheet("""QLabel{color:rgb(39, 39, 39)}
#                             QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#                 else:
#                     self.msg.setStyleSheet("""QLabel{color:rgb(238, 248, 255)}
#                             QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#
#                 self.msg.setText("Unable to parse the file format")
#                 self.msg.show()
#                 return 1
#
#         else:
#             self.edit_input_xml.setText('No file selected')
#         return 0
#
#     def openFolderWindow(self):
#         self.folder_name = ""
#         self.folderWindow = _FolderWindow()
#
#         if self.screenWidth <= 2400 or self.screenHeight <= 1200:
#             self.folderWindow.resize(300,150)
#         else:
#             self.folderWindow.resize(600,300)
#
#         if self.theme == "Light":
#             '''
#             #dark blue
#             self.folderWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.folderWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}""")
#         else:
#             self.folderWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}""")
#         self.folderWindow.show()
#         self.folderWindow.mainWindow = self
#
#     def output_xml(self):
#         self.filename_output = QFileDialog.getSaveFileName(self, 'Select Output GML')[0]
#         print("OutputGML=",self.filename_output)
#         if self.filename_output:
#             self.edit_output_xml.setText(self.filename_output)
#         else:
#             self.edit_output_xml.setText('No file selected')
#         return 0
#
#     def openTransformationWindow(self):
#         self.transformationWindow = _TransformationWindow()
#         self.transformationWindow.inputFileName = self.edit_input_xml.text()
#         self.transformationWindow.outputFileName = self.folder_name+"/Transformation_Result.gml"
#         self.transformationWindow.resize(self.w, self.h)
#         if self.cmb_theme.currentText() == "Light        ":
#             '''
#             #dark blue
#             self.transformationWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}\
#                 QCheckBox{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.transformationWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}\
#                 QCheckBox{color:rgb(39, 39, 39)}""")
#         else:
#             self.transformationWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}\
#                 QCheckBox{color:rgb(238, 248, 255)}""")
#         self.transformationWindow.show()
#         self.transformationWindow.mainWindow = self
#
#         self.hide()
#         #stop animation
#         self.animation.stop()
#         self.btn_transform_xml.reset_color()
#
#     def openDrawWindow(self):
#         self.drawWindow = _DrawWindow()
#         self.drawWindow.inputFileName = self.edit_input_xml.text()
#         self.drawWindow.outputFileName = self.folder_name+"/Transformation_Result.gml"
#         self.drawWindow.resize(self.w, self.h)
#         if self.cmb_theme.currentText() == "Light        ":
#             self.drawWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}""")
#         else:
#             self.drawWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}""")
#         #---------------------------------------------------------
#         self.drawWindow.show()
#         self.drawWindow.mainWindow = self
#         self.hide()
#
#
#     def openValidationWindow(self):
#         self.validationWindow = _ValidationWindow()
#         self.validationWindow.inputFileName = self.edit_input_xml.text()
#         self.validationWindow.outputFileName = self.folder_name+"/Transformation_Result.gml"
#         self.validationWindow.resize(self.w, self.h)
#         if self.cmb_theme.currentText() == "Light        ":
#             '''
#             #dark blue
#             self.validationWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.validationWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}""")
#         else:
#             self.validationWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}""")
#         self.validationWindow.show()
#         self.validationWindow.mainWindow = self
#         self.hide()
#
#
#     def openCropWindow(self):
#         self.cropWindow = _CropWindow()
#         #self.cropWindow.inputFileName = self.edit_input_xml.text()
#         #self.cropWindow.edit_input_xml.setText(self.cropWindow.inputFileName)
#         self.cropWindow.resize(self.w, self.h)
#         if self.theme == "Light":
#             '''
#             #dark blue
#             self.cropWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}\
#                 QCheckBox{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.cropWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}\
#                 QCheckBox{color:rgb(39, 39, 39)}""")
#         else:
#             self.cropWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}\
#                 QCheckBox{color:rgb(238, 248, 255)}""")
#         self.cropWindow.show()
#         self.cropWindow.mainWindow = self
#         self.hide()
#
#     def aboutThisTool(self):
#         # open your URL
#         url = QUrl('http://gitlab.com')
#         try:
#             QDesktopServices.openUrl(url)
#         except:
#             self.raise_warnings('Network error: No connection', 'Please check your network connection.')
#
#     def close_application(self):
#         self.exitQuestionWindow = _ExitQuestionWindow()
#         if self.screenWidth <= 2400 or self.screenHeight <= 1200:
#             self.exitQuestionWindow.resize(300,80)
#         else:
#             self.exitQuestionWindow.resize(600,160)
#
#         self.exitQuestionWindow.setStyleSheet("background-color:rgb(255, 250, 240); color:black")
#         self.exitQuestionWindow.show()
#
# # **********************************************************************************
# class _FolderWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_FolderWindow,self).__init__(parent)
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle("Create your Folder")
#
#         self.mainWindow = _MainWindow()
#
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#
#         # a label and two button
#         self.vbox = QVBoxLayout()
#         self.setLayout(self.vbox)
#
#         self.lbl_folder_name = QLabel("Please enter your folder name")
#         self.lbl_folder_name.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.lbl_folder_name)
#
#         self.edit_folder_name = QLineEdit("CityGML_Transformation_Output")
#         self.edit_folder_name.setFont(self.mySlimFont)
#         self.vbox.addWidget(self.edit_folder_name)
#
#         self.btn_create = QPushButton("Create this Folder")
#         self.btn_create.setFont(self.myBoldFont)
#         self.btn_create.setStyleSheet("background-color:rgb(238, 248, 255)")
#         self.vbox.addWidget(self.btn_create)
#         self.btn_create.clicked.connect(self.createFolder)
#
#         self.btn_back = QPushButton("Back")
#         self.btn_back.setFont(self.myBoldFont)
#         self.btn_back.setStyleSheet("background-color:rgb(174, 163, 163)")
#         self.vbox.addWidget(self.btn_back)
#         self.btn_back.clicked.connect(self.close)
#
#     def createFolder(self):
#         self.folder_name = self.mainWindow.workingDirectory +"/"+ self.edit_folder_name.text()
#
#         try:
#             os.mkdir(self.folder_name)
#             self.mainWindow.folder_name = self.folder_name
#             self.mainWindow.edit_select_folder.setText (self.folder_name)
#
#             self.msgBoxCreator("Folder Created!")
#             # stop animation
#             self.mainWindow.animation.stop()
#             self.mainWindow.btn_create_folder.reset_color()
#             self.mainWindow.animButton(self.mainWindow.btn_transform_xml)
#
#             #Enable buttons
#             self.mainWindow.btn_transform_xml.setEnabled(True)
#             self.mainWindow.btn_transform_xml.setStyleSheet("background-color:rgb(238, 248, 255)")
#             self.mainWindow.btn_draw_xml.setEnabled(True)
#             self.mainWindow.btn_draw_xml.setStyleSheet("background-color:rgb(238, 248, 255)")
#             self.mainWindow.btn_validate_xml.setEnabled(True)
#             self.mainWindow.btn_validate_xml.setStyleSheet("background-color:rgb(238, 248, 255)")
#             self.close()
#         except:
#             self.msgBoxCreator("Unable to create folder!")
#             return 1
#
#     # create a QMessageBox when needed
#     def msgBoxCreator(self,text):
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText(text)
#         self.msg.show()
#
# class _ExitQuestionWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_ExitQuestionWindow,self).__init__(parent)
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle("")
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         # a label and two button
#         self.vbox = QVBoxLayout()
#         self.setLayout(self.vbox)
#
#         self.lbl_exit_question = QLabel("Do you really want to quit?")
#         self.lbl_exit_question.setFont(self.myBoldFont)
#         self.vbox.addWidget(self.lbl_exit_question)
#
#         self.hbox = QHBoxLayout()
#         self.vbox.addLayout(self.hbox)
#
#         self.btn_yes = QPushButton("Confirm")
#         self.btn_yes.setFont(self.myBoldFont)
#         self.btn_yes.setStyleSheet("background-color:rgb(238, 248, 255)")
#         self.btn_yes.setFont(self.myBoldFont)
#         self.btn_yes.clicked.connect(self.exitConfirmed)
#         self.hbox.addWidget(self.btn_yes)
#
#         self.btn_no = QPushButton("Cancel")
#         self.btn_no.setFont(self.myBoldFont)
#         self.btn_no.setStyleSheet("background-color:rgb(174, 163, 163)")
#         self.btn_no.setFont(self.myBoldFont)
#         self.btn_no.clicked.connect(self.exitCanceled)
#         self.hbox.addWidget(self.btn_no)
#
#     def exitConfirmed(self):
#         sys.exit()
#
#     def exitCanceled(self):
#         self.close()
#
# # **********************************************************************************
# class _CropWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_CropWindow, self).__init__(parent)
#
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle('Crop Buildings')
#
#         # save the mainWindow
#         self.mainWindow = _MainWindow()
#
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         # Data
#         # file names for validation
#         self.inputFileName = ""
#         self.outputFileName = ""
#         # building selection list
#         self.buildingSelectionList = []
#         # all buildings
#         self.buildingList = []
#         # UI
#         # base layout
#         self.vbox_crop = QVBoxLayout()
#         self.setLayout(self.vbox_crop)
#
#         # Input file
#         self.btn_input_xml = QPushButton("Input XML/GML File")
#         self.btn_input_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_input_xml.setFont(self.myBoldFont)
#         self.btn_input_xml.clicked.connect(self.input_xml)
#         self.vbox_crop.addWidget(self.btn_input_xml)
#         # label to display input fileName and number of Buildings.
#         self.edit_input_xml = QLineEdit()
#         self.edit_input_xml.setEnabled(False)
#         self.edit_input_xml.setStyleSheet("background-color: rgb(180, 190, 210); color: black ")
#         self.edit_input_xml.setFont(self.mySlimFont)
#         self.vbox_crop.addWidget(self.edit_input_xml)
#
#         #input information
#         self.hbox_NumberOfBuilding = QHBoxLayout()
#         self.vbox_crop.addLayout(self.hbox_NumberOfBuilding)
#         self.lbl_NumberOfBuilding = QLabel("Number of Buildings =")
#         self.lbl_NumberOfBuilding.setFont(self.myBoldFont)
#         self.edit_NumberOfBuilding = QLineEdit()
#         self.edit_NumberOfBuilding.setEnabled(False)
#         self.edit_NumberOfBuilding.setFont(self.mySlimFont)
#         self.edit_NumberOfBuilding.setStyleSheet("background-color: rgb(180, 190, 210); color: black")
#
#         self.lbl_version = QLabel("CityGML Version =")
#         self.lbl_version.setFont(self.myBoldFont)
#         self.edit_version = QLineEdit()
#         self.edit_version.setEnabled(False)
#         self.edit_version.setFont(self.mySlimFont)
#         self.edit_version.setStyleSheet("background-color: rgb(180, 190, 210); color: black")
#
#         self.hbox_NumberOfBuilding.addWidget(self.lbl_NumberOfBuilding)
#         self.hbox_NumberOfBuilding.addWidget(self.edit_NumberOfBuilding)
#         self.hbox_NumberOfBuilding.addWidget(self.lbl_version)
#         self.hbox_NumberOfBuilding.addWidget(self.edit_version)
#
#         # Output file
#         self.btn_output_xml = QPushButton("Output XML/GML File")
#         self.btn_output_xml.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_output_xml.setFont(self.myBoldFont)
#         self.btn_output_xml.clicked.connect(self.output_xml)
#         self.vbox_crop.addWidget(self.btn_output_xml)
#         # label to display input fileName and number of Buildings.
#         self.edit_output_xml = QLineEdit()
#         self.edit_output_xml.setEnabled(False)
#         self.edit_output_xml.setStyleSheet("background-color: rgb(180, 190, 210); color: black ")
#         self.edit_output_xml.setFont(self.mySlimFont)
#         self.vbox_crop.addWidget(self.edit_output_xml)
#
#         # set up the number of buildings to be cropped in the output file
#         self.gbox_random_setting = QGroupBox()
#         self.vbox_crop.addWidget(self.gbox_random_setting)
#         self.vbox_random_setting = QVBoxLayout()
#         self.gbox_random_setting.setLayout(self.vbox_random_setting)
#
#         self.checkbox_random_setting = QCheckBox("Randomly Crop Buildings from Input File")
#         self.checkbox_random_setting.setFont(self.mySlimFont)
#         self.checkbox_random_setting.setChecked(False)
#         self.vbox_random_setting.addWidget(self.checkbox_random_setting)
#
#         self.hbox_random_setting = QHBoxLayout()
#         self.vbox_random_setting.addLayout(self.hbox_random_setting)
#         # label and editor
#         self.lbl_random_setting = QLabel("Enter the number of buildings to crop:")
#         self.lbl_random_setting.setFont(self.myBoldFont)
#         self.hbox_random_setting.addWidget(self.lbl_random_setting)
#         self.edit_random_setting = QLineEdit("1")
#         self.edit_random_setting.setFont(self.myBoldFont)
#         self.hbox_random_setting.addWidget(self.edit_random_setting)
#
#         self.edit_random_setting.setEnabled(False)
#         self.checkbox_random_setting.toggled.connect(lambda: self.checkState("Random"))
#
#         # Manually Crop Module
#         self.gbox_manual_setting = QGroupBox()
#         self.vbox_manual_setting = QVBoxLayout()
#         self.gbox_manual_setting.setLayout(self.vbox_manual_setting)
#         self.vbox_crop.addWidget(self.gbox_manual_setting)
#
#         self.checkbox_manual_setting = QCheckBox("Manually Select Buildings to Crop")
#         self.checkbox_manual_setting.setChecked(False)
#         self.checkbox_manual_setting.setFont(self.mySlimFont)
#         self.vbox_manual_setting.addWidget(self.checkbox_manual_setting)
#
#         self.checkbox_manual_setting.toggled.connect(lambda: self.checkState("Manual"))
#
#         # label to indicate the number of building selected
#         self.lbl_manual_setting_number = QLabel("Number of Buildings Selected = 0")
#         self.lbl_manual_setting_number.setFont(self.myBoldFont)
#         self.btn_selectedBuildigs = QPushButton("Edit Selection")
#         self.btn_selectedBuildigs.setFont(self.myBoldFont)
#         self.btn_selectedBuildigs.clicked.connect(self.openBuildingListWindow)
#         self.btn_selectedBuildigs.setEnabled(False)
#
#         self.hbox_selectedBuildings = QHBoxLayout()
#         self.vbox_manual_setting.addLayout(self.hbox_selectedBuildings)
#         self.hbox_selectedBuildings.addWidget(self.lbl_manual_setting_number)
#         self.hbox_selectedBuildings.addWidget(self.btn_selectedBuildigs)
#         #---------------------------------------------------
#         # button to crop
#         self.btn_crop = QPushButton("Crop")
#         self.btn_crop.setStyleSheet(
#                 """QPushButton { background-color: rgb(238, 248, 255); color: black}""")
#         self.btn_crop.setFont(self.myBoldFont)
#         self.btn_crop.clicked.connect(self.cropXML)
#         self.vbox_crop.addWidget(self.btn_crop)
#
#         # close it
#         self.btn_exit_crop = QPushButton("Back")
#         self.btn_exit_crop.setFont(self.myBoldFont)
#         self.btn_exit_crop.clicked.connect(self.close_window)
#         self.btn_exit_crop.setStyleSheet("background-color:rgb(174, 163, 163)")
#         self.vbox_crop.addWidget(self.btn_exit_crop)
#
#
#     def openBuildingListWindow(self):
#         # open a BuildingListWindow
#         self.buildingListWindow = BuildingListWindow()
#         self.buildingListWindow.mainWindow = self
#         self.buildingListWindow.resize(300,300)
#
#         # set up search List
#         for building in self.buildingList:
#             self.buildingListWindow.buildingNameList.append(str(building.name).split("'")[-2])
#         #print(self.buildingListWindow.buildingNameList)
#
#         self.buildingListWindow.buildingQueue.setStringList(self.buildingListWindow.buildingNameList)
#         self.buildingListWindow.searchCompleter = QCompleter()
#         self.buildingListWindow.searchCompleter.setModel(self.buildingListWindow.buildingQueue)
#         self.buildingListWindow.searchBar.setCompleter(self.buildingListWindow.searchCompleter)
#
#         for item in self.buildingSelectionList:
#             self.buildingListWindow.lst_building.addItem(item)
#
#         # theme
#         if self.mainWindow.theme == "Light":
#             '''
#             #dark blue
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240)}
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240)}
#                 QLabel{color:rgb(39, 39, 39)}""")
#
#             self.buildingListWindow.lst_building.setStyleSheet("""QListWidget{background-color:rgb(240,240,240)}
#                         QListWidget::Item:hover{background:skyblue; }
#                         QListWidget::item:selected:!active{border-width:0px; background:lightgreen;}""")
#         else:
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30)}
#                 QLabel{color:rgb(238, 248, 255)}""")
#             self.buildingListWindow.lst_building.setStyleSheet("""QListWidget{background-color:rgb(130,145,150)}
#                         QListWidget::Item:hover{background:skyblue; }
#                         QListWidget::item:selected:!active{border-width:0px; background:lightgreen;}""")
#
#         self.buildingListWindow.show()
#         self.hide()
#
#     def checkState(self, cropOption):
#         if cropOption == "Random":
#             if self.checkbox_random_setting.isChecked():
#                 self.checkbox_manual_setting.setChecked(False)
#                 self.edit_random_setting.setEnabled(True)
#             else:
#                 self.edit_random_setting.setEnabled(False)
#         else:
#             if self.checkbox_manual_setting.isChecked():
#                 self.checkbox_random_setting.setChecked(False)
#                 self.btn_selectedBuildigs.setEnabled(True)
#             else:
#                 self.btn_selectedBuildigs.setEnabled(False)
#     # input file operation, get the file name
#     def input_xml(self):
#         self.inputFileName = QFileDialog.getOpenFileName(self, 'Select Input XML')[0]
#         print("InputXML=",self.inputFileName)
#         if self.inputFileName:
#             # erase existing buildingSelectionList
#             self.buildingSelectionList = []
#             self.lbl_manual_setting_number.setText("Number of Buildings Selected = 0")
#             # determine _nameSpace for XML parser
#             self.version = 0
#             try:
#                 with open(self.inputFileName,"r") as fileHandle:
#                     for line in fileHandle.readlines():
#                         if str(line).find("citygml/1.0")!= -1:
#                             self._nameSpace = self.mainWindow._nameSpace1
#                             self.version = 1
#                             print("CityGml Version = 1.0")
#                             break
#                         elif str(line).find("citygml/2.0")!= -1:
#                             self._nameSpace = self.mainWindow._nameSpace2
#                             self.version = 2
#                             print("CityGML Version = 2.0")
#                             break
#                     # end loop
#                     if self.version == 0:
#                         print("CityGML Version Not Supported.")
#                         return -1
#
#                 self.buildingList = readCityGML(self.inputFileName,self._nameSpace)
#                 self.edit_input_xml.setText(self.inputFileName)
#                 self.edit_NumberOfBuilding.setText(str(len(self.buildingList)))
#                 self.edit_version.setText(str(self.version)+".0")
#             except:
#                 self.msgBoxCreator("Unable to parse the file!")
#         else:
#             self.edit_input_xml.setText('No file selected')
#         return 0
#
#     def output_xml(self):
#         self.outputFileName = QFileDialog.getSaveFileName(self, 'Select output XML')[0]
#         print("OutputXML=",self.outputFileName)
#         if self.outputFileName:
#             self.edit_output_xml.setText(self.outputFileName)
#         else:
#             self.edit_output_xml.setText('No file selected')
#         return 0
#
#     def cropXML(self):
#         if self.checkbox_random_setting.isChecked():
#             print("Randomly Crop XML/GML...")
#             self.randomCrop()
#
#         elif self.checkbox_manual_setting.isChecked():
#             print("Manually Crop XML/GML...")
#             self.manualCrop()
#
#         else:
#             self.msgBoxCreator("Please check one option (Random or Manual)!")
#             return 0
#
#     def randomCrop(self):
#         try:
#             numBldg = int(self.edit_random_setting.text())
#         except:
#             self.msgBoxCreator("Please enter integer number!")
#             return 1
#
#         try:
#             tree = ET.parse(self.inputFileName)
#             root = tree.getroot()
#         except:
#             self.msgBoxCreator("Input file does not exist!")
#             return 1
#
#         bldg_counter = 0
#         counter_i = 0
#         buildingList = readCityGML(self.inputFileName,self._nameSpace)
#         for cityObj in root.findall(".//core:cityObjectMember",self._nameSpace):
#             counter_i += 1
#             # percentage to determine whether a building will be removed or not
#             percent = 50
#             if bldg_counter >= numBldg:
#                 root.remove(cityObj)
#                 continue
#             if random.random()*100 < percent and len(buildingList)-counter_i>numBldg - bldg_counter:
#                 root.remove(cityObj)
#             else:
#                 bldg_counter += 1
#
#
#         # use tree.write directly, instead of using treeWriter(). Thus, register is necessary.
#         for key in self._nameSpace.keys():
#             ET.register_namespace(str(key),str(self._nameSpace[key]))
#
#         try:
#             tree.write(self.outputFileName,xml_declaration=True,encoding='utf-8', method="xml")
#         except:
#             self.msgBoxCreator("Output XML/GML does not exist!")
#             return 1
#
#         #finish
#         self.msgBoxCreator("Crop Completed!")
#         return 0
#
#     def manualCrop(self):
#         try:
#             tree = ET.parse(self.inputFileName)
#             root = tree.getroot()
#         except:
#             self.msgBoxCreator("Input file does not exist!")
#             return 1
#
#         for cityObj in root.findall(".//core:cityObjectMember",self._nameSpace):
#             for bldg in cityObj.findall(".//bldg:Building",self._nameSpace):
#                 buildingName = str(bldg.attrib).split("'")[-2]
#                 if buildingName in self.buildingSelectionList:
#                     continue
#                 else:
#                     root.remove(cityObj)
#                     break
#
#         # use tree.write directly, instead of using treeWriter(). Thus, register is necessary.
#         for key in self._nameSpace.keys():
#             ET.register_namespace(str(key),str(self._nameSpace[key]))
#
#         try:
#             tree.write(self.outputFileName,xml_declaration=True,encoding='utf-8', method="xml")
#         except:
#             self.msgBoxCreator("Output XML/GML does not exist!")
#             return 1
#
#         #finish
#         self.msgBoxCreator("Crop Completed!")
#         return 0
#
#     # create a QMessageBox when needed
#     def msgBoxCreator(self,text):
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText(text)
#         self.msg.show()
#
#     # method to close current window and back to the Main Window.
#     def close_window(self):
#         # back to mainWindow and close the sub-window.
#         self.mainWindow.show()
#         self.close()
#         return 0
#
#
# # **********************************************************************************
# class BuildingListWindow(QDialog):
#     def __init__(self, parent=None):
#         super(BuildingListWindow, self).__init__(parent)
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#
#         self.mainWindow = _CropWindow()
#         self.setWindowTitle('Edit Selection of buildings')
#
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         # Data
#         # use .setStringList(self.buildingNameList) to set its content.
#         # self.buildingNameList is the complete set of all the building names of the input file.
#         self.buildingQueue = QStringListModel()
#         self.buildingNameList = []
#
#         # UI
#         self.vbox_bList = QVBoxLayout()
#         self.setLayout(self.vbox_bList)
#
#         # search bar is just a lineEdit
#         self.searchBar = QLineEdit("Search")
#         self.searchBar.setFont(self.mySlimFont)
#         self.searchBar.setStyleSheet("color:rgb(180,180,180)")
#         self.searchBar.setAlignment(Qt.AlignCenter)
#         self.searchBar.textChanged.connect(self.searchBarColorChange)
#
#         self.btn_addBuilding = QPushButton("Add")
#         self.btn_addBuilding.setFont(self.myBoldFont)
#         self.btn_addBuilding.clicked.connect(self.addBuilding)
#
#         self.hbox_search = QHBoxLayout()
#         self.hbox_search.addWidget(self.searchBar)
#         self.hbox_search.addWidget(self.btn_addBuilding)
#         self.vbox_bList.addLayout(self.hbox_search)
#
#         self.lbl_bList = QLabel("List of selected buildings:")
#         self.lbl_bList.setFont(self.myBoldFont)
#         self.vbox_bList.addWidget(self.lbl_bList)
#
#         self.lst_building = QListWidget()
#         self.vbox_bList.addWidget(self.lst_building)
#         self.lst_building.setFont(self.myBoldFont)
#         self.lst_building.setSelectionMode(QAbstractItemView.ExtendedSelection)
#
#         #delete building
#         self.btn_delete = QPushButton("Delete")
#         self.btn_delete.setFont(self.myBoldFont)
#         self.btn_delete.setStyleSheet("background-color:rgb(250,150,40)")
#         self.btn_delete.clicked.connect(self.deleteBuilding)
#         self.vbox_bList.addWidget(self.btn_delete)
#
#         #back to parent window
#         self.btn_back = QPushButton("OK")
#         self.btn_back.setFont(self.myBoldFont)
#         self.btn_back.setStyleSheet("background-color:rgb(174, 163, 163)")
#         self.btn_back.clicked.connect(self.close_window)
#         self.vbox_bList.addWidget(self.btn_back)
#
#     def addBuilding(self):
#         newBuildingName = self.searchBar.text()
#         if newBuildingName in \
#         [str(self.lst_building.item(i).text()) for i in range(self.lst_building.count())]:
#             self.msgBoxCreator("This building has alrady been selected!")
#             return 0
#         elif newBuildingName in self.buildingNameList:
#             # now add it to the listWidget
#             self.lst_building.addItem(newBuildingName)
#         else:
#             self.msgBoxCreator("Building does not exist!")
#             return 1
#
#     def deleteBuilding(self):
#         selectedItemList = self.lst_building.selectedItems()
#         for item in selectedItemList:
#             #print(str(item))
#             try:
#                 self.lst_building.takeItem(self.lst_building.row(item))
#             except:
#                 self.msgBoxCreator("Fail to delete item(s).")
#
#     def searchBarColorChange(self):
#         self.searchBar.setStyleSheet("color:black")
#
#     def close_window(self,label):
#         # back to mainWindow and close the sub-window.
#         self.mainWindow.lbl_manual_setting_number.\
#             setText("Number of Buildings Selected = "+str(self.lst_building.count()))
#         # mainWindow must have a property named "buildingSelectionList"
#         self.mainWindow.buildingSelectionList = \
#             [str(self.lst_building.item(i).text()) for i in range(self.lst_building.count())]
#
#         self.mainWindow.show()
#         self.close()
#         return 0
#
#         # create a QMessageBox when needed
#     def msgBoxCreator(self,text):
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText(text)
#         self.msg.show()
#
# #**********************************************************************************
# class _TransformationWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_TransformationWindow, self).__init__(parent)
#
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle('CRS Transformation')
#
#         # save the mainWindow
#         self.mainWindow = _MainWindow()
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         # Data
#         # file names for validation
#         self.inputFileName = ""
#         self.outputFileName = ""
#         self.buildingSelectionList = []
#
#         # UI
#         # base layout
#         self.vbox_transformation = QVBoxLayout()
#         self.setLayout(self.vbox_transformation)
#
#         # epsg settings
#         self.gbox_crs_settings = QGroupBox("")
#         #self.gbox_crs_settings.setStyleSheet("font-weight: bold;")
#         self.grid_crs_settings = QGridLayout()
#         self.gbox_crs_settings.setLayout(self.grid_crs_settings)
#         self.vbox_transformation.addWidget(self.gbox_crs_settings)
#
#         self.lbl_input_crs = QLabel("Input CRS")
#         self.lbl_input_crs.setFont(self.myBoldFont)
#         self.lbl_output_crs = QLabel("Output CRS")
#         self.lbl_output_crs.setFont(self.myBoldFont)
#         self.grid_crs_settings.addWidget(self.lbl_input_crs,0,0)
#         self.grid_crs_settings.addWidget(self.lbl_output_crs,0,1)
#         #self.edit_input_crs = QLineEdit('epsg:5555')
#         #self.edit_output_crs = QLineEdit('epsg:27700')
#         epsgList = ['epsg:5555 DE','epsg:5834 DE','epsg:23032 EU','epsg:25832 EU','epsg:27700 UK']
#         self.cmb_input_crs = QComboBox()
#         self.cmb_input_crs.addItems(epsgList)
#         self.cmb_input_crs.setStyleSheet("color: black")
#         self.cmb_input_crs.setFont(self.myBoldFont)
#
#         self.cmb_output_crs = QComboBox()
#         self.cmb_output_crs.addItems(epsgList)
#         self.cmb_output_crs.setFont(self.myBoldFont)
#
#         self.grid_crs_settings.addWidget(self.cmb_input_crs,1,0)
#         self.grid_crs_settings.addWidget(self.cmb_output_crs,1,1)
#         #------------------------------------------------------------------------
#         #tragetpoint for transformation
#         self.gbox_targetPoint = QGroupBox()
#         self.vbox_transformation.addWidget(self.gbox_targetPoint)
#         self.vbox_targetPoint = QVBoxLayout()
#         self.gbox_targetPoint.setLayout(self.vbox_targetPoint)
#
#         self.lbl_lonlat = QLabel("Please edit your Destination here: [Lon,Lat] from EPSG 4326 (in Degree)")
#         self.setFont(self.myBoldFont)
#         self.vbox_targetPoint.addWidget(self.lbl_lonlat)
#
#         self.hbox_lonlat = QHBoxLayout()
#         self.vbox_targetPoint.addLayout(self.hbox_lonlat)
#
#         self.lbl_lon = QLabel("Lon=")
#         self.lbl_lon.setFont(self.myBoldFont)
#         self.edit_lon = QLineEdit("-0.08818")
#         self.edit_lon.setStyleSheet(\
#             "background-color:rgb(180,190,210);")
#         self.edit_lon.setFont(self.mySlimFont)
#
#         self.lbl_lat = QLabel("Lat=")
#         self.lbl_lat.setFont(self.myBoldFont)
#         self.edit_lat = QLineEdit("51.489767")
#         self.edit_lat.setStyleSheet(\
#             "background-color:rgb(180,190,210);")
#         self.edit_lat.setFont(self.mySlimFont)
#
#         self.btn_lonlat = BlinkButton("Transform to [X,Y,Z]")
#         self.btn_lonlat.setFont(self.myBoldFont)
#         self.btn_lonlat.clicked.connect(self.transformLonLat)
#         self.btn_lonlat.setStyleSheet("font:bold;background-color:rgb(238, 248, 255);font-weight:bold")
#
#         self.animButton(self.btn_lonlat)
#
#         self.hbox_lonlat.addWidget(self.lbl_lat)
#         self.hbox_lonlat.addWidget(self.edit_lat)
#         self.hbox_lonlat.addWidget(self.lbl_lon)
#         self.hbox_lonlat.addWidget(self.edit_lon)
#         self.hbox_lonlat.addWidget(self.btn_lonlat)
#
#         self.tragetpoint = [0,0,0]
#         # contains one label and 3 lineEdits
#         self.lbl_tartgetPoint = \
#             QLabel("\nDestination in [x,y,z]\nCoordinates shall fall within the projeced bounds of output CRS.")
#         self.setFont(self.myBoldFont)
#         self.vbox_targetPoint.addWidget(self.lbl_tartgetPoint)
#
#         # hbox  for 3 lineEdits, [x],[y],[z]
#         self.hbox_targpoint = QHBoxLayout()
#         self.vbox_targetPoint.addLayout(self.hbox_targpoint)
#
#
#         self.lbl_x = QLabel("X=")
#         self.lbl_x.setFont(self.myBoldFont)
#         self.edit_targetPoint_x = QLineEdit("--")
#         self.edit_targetPoint_x.setStyleSheet(\
#             "background-color:rgb(180,190,210);")
#         self.edit_targetPoint_x.setFont(self.mySlimFont)
#         self.edit_targetPoint_x.setEnabled(False)
#
#         self.lbl_y = QLabel("Y=")
#         self.lbl_y.setFont(self.myBoldFont)
#         self.edit_targetPoint_y = QLineEdit("--")
#         self.edit_targetPoint_y.setStyleSheet(\
#             "background-color:rgb(180,190,210);")
#         self.edit_targetPoint_y.setFont(self.mySlimFont)
#         self.edit_targetPoint_y.setEnabled(False)
#
#         self.lbl_z = QLabel("Z=")
#         self.lbl_z.setFont(self.myBoldFont)
#         self.edit_targetPoint_z = QLineEdit("0")
#         self.edit_targetPoint_z.setStyleSheet(\
#             "background-color:rgb(180,190,210);")
#         self.edit_targetPoint_z.setFont(self.mySlimFont)
#         self.edit_targetPoint_z.setEnabled(False)
#
#         self.hbox_targpoint.addWidget(self.lbl_x)
#         self.hbox_targpoint.addWidget(self.edit_targetPoint_x)
#         self.hbox_targpoint.addWidget(self.lbl_y)
#         self.hbox_targpoint.addWidget(self.edit_targetPoint_y)
#         self.hbox_targpoint.addWidget(self.lbl_z)
#         self.hbox_targpoint.addWidget(self.edit_targetPoint_z)
#         #------------------------------------------------------------------------
#
#         # rotation module
#         self.gbox_rotation = QGroupBox()
#         self.vbox_transformation.addWidget(self.gbox_rotation)
#         self.vbox_rotation = QVBoxLayout()
#         self.gbox_rotation.setLayout(self.vbox_rotation)
#
#         self.hbox_checkbox = QHBoxLayout()
#         self.checkbox_rotation = QCheckBox("Enable Rotation Transformation")
#         self.checkbox_rotation.setFont(self.mySlimFont)
#         self.checkbox_rotation.setChecked(False)
#         self.hbox_checkbox.addWidget(self.checkbox_rotation)
#
#
#         self.btn_help = BlinkButton("Help")
#         self.btn_help.resize(20,20)
#         self.btn_help.setFont(self.myBoldFont)
#         self.btn_help.clicked.connect(self.openInfoWindow)
#         self.btn_help.setStyleSheet("font:bold;background-color:rgb(174, 163, 163);font-weight:bold")
#         self.hbox_checkbox.addStretch(4)
#         self.hbox_checkbox.addWidget(self.btn_help)
#
#         self.lbl_rotation = QLabel("Use Central of your Input CityGML as Pivot Point")
#         self.lbl_rotation.setFont(self.myBoldFont)
#
#         self.hbox_rotation = QHBoxLayout()
#         self.lbl_rotation_angle = QLabel("Please Enter Rotation Angle in Degree[-360,360]:")
#         self.lbl_rotation_angle.setFont(self.myBoldFont)
#         self.hbox_rotation.addWidget(self.lbl_rotation_angle)
#         self.edit_rotation = QLineEdit("0")
#         self.edit_rotation.setFont(self.mySlimFont)
#         self.hbox_rotation.addWidget(self.edit_rotation)
#
#         self.edit_rotation.setEnabled(False)
#         self.checkbox_rotation.toggled.connect(self.checkRotation)
#
#         self.vbox_rotation.addLayout(self.hbox_checkbox)
#         self.vbox_rotation.addWidget(self.lbl_rotation)
#         self.vbox_rotation.addLayout(self.hbox_rotation)
#
#         #------------------------------------------------------------------------
#         # elevation module
#         self.gbox_elevation = QGroupBox()
#         #self.checkbox_elevation.toggled.connect(self.gbox_elevation.setEnabled)
#         self.vbox_transformation.addWidget(self.gbox_elevation)
#         self.vbox_elevation = QVBoxLayout()
#         self.gbox_elevation.setLayout(self.vbox_elevation)
#
#         self.hbox_checkbox2 = QHBoxLayout()
#         self.checkbox_elevation = QCheckBox("Enable Elevation Transformation")
#         self.checkbox_elevation.setFont(self.mySlimFont)
#         self.checkbox_elevation.setChecked(False)
#         self.hbox_checkbox2.addWidget(self.checkbox_elevation)
#
#         self.btn_help2 = BlinkButton("Help")
#         self.btn_help2.resize(20,20)
#         self.btn_help2.setFont(self.myBoldFont)
#         self.btn_help2.clicked.connect(self.openInfoWindowE)
#         self.btn_help2.setStyleSheet("font:bold;background-color:rgb(174, 163, 163);font-weight:bold")
#         self.hbox_checkbox2.addStretch(4)
#         self.hbox_checkbox2.addWidget(self.btn_help2)
#
#         self.hbox_elevation = QHBoxLayout()
#         self.lbl_elevation = QLabel("Please Enter Elevation Change Value in [m]:")
#         self.lbl_elevation.setFont(self.myBoldFont)
#         self.hbox_elevation.addWidget(self.lbl_elevation)
#         self.edit_elevation = QLineEdit("0")
#         self.edit_elevation.setFont(self.mySlimFont)
#         self.hbox_elevation.addWidget(self.edit_elevation)
#
#         self.edit_elevation.setEnabled(False)
#         self.checkbox_elevation.toggled.connect(self.checkElevation)
#
#         self.vbox_elevation.addLayout(self.hbox_checkbox2)
#         self.vbox_elevation.addLayout(self.hbox_elevation)
#
#         # building Selection module
#         self.gbox_buildingSelection = QGroupBox()
#         self.vbox_transformation.addWidget(self.gbox_buildingSelection)
#         self.vbox_buildingSelection = QVBoxLayout()
#         self.gbox_buildingSelection.setLayout(self.vbox_buildingSelection)
#
#         self.checkbox_buildingSelection = \
#             QCheckBox("Enable Building Selection for Rotation/Elevation Transformation\nUncheck to Apply Transformation to All Buildings.")
#         self.checkbox_buildingSelection.setFont(self.mySlimFont)
#         self.vbox_buildingSelection.addWidget(self.checkbox_buildingSelection)
#
#         # careful don't mix up with the hbox in CropWindow
#         self.hbox_buildingSelection = QHBoxLayout()
#         self.vbox_buildingSelection.addLayout(self.hbox_buildingSelection)
#         self.lbl_manual_setting_number = QLabel("Number of Buildings Selected = ALL")
#         self.lbl_manual_setting_number.setFont(self.myBoldFont)
#         self.btn_buildingSelection = QPushButton("Edit Selection")
#         self.btn_buildingSelection.setFont(self.myBoldFont)
#         self.btn_buildingSelection.clicked.connect(self.openBuildingListWindow)
#         self.btn_buildingSelection.setEnabled(False)
#
#         self.checkbox_buildingSelection.toggled.connect(self.onToggleBuildingSelection)
#
#         self.hbox_buildingSelection.addWidget(self.lbl_manual_setting_number)
#         self.hbox_buildingSelection.addWidget(self.btn_buildingSelection)
#         #------------------------------------------------------------
#         # progressBar
#         self.progressBar = QProgressBar()
#         self.vbox_transformation.addWidget(self.progressBar)
#         self.progressBar.setRange(0, 100)
#         self.progressBar.setValue(0)
#
#         # button to start
#         self.btn_transform_xml = QPushButton("Start Transformation")
#         self.btn_transform_xml.setFont(self.myBoldFont)
#         self.btn_transform_xml.clicked.connect(self.transformXML)
#         self.btn_transform_xml.setStyleSheet("font:bold;background-color:rgb(238, 248, 255);font-weight:bold")
#         self.vbox_transformation.addWidget(self.btn_transform_xml)
#
#         # close it
#         self.btn_exit_transformation = QPushButton("Back")
#         self.btn_exit_transformation.setFont(self.myBoldFont)
#         self.btn_exit_transformation.clicked.connect(self.close_window)
#         self.btn_exit_transformation.setStyleSheet("font:bold;background-color:rgb(174, 163, 163);font-weight:bold")
#         self.vbox_transformation.addWidget(self.btn_exit_transformation)
#
#         # disable check boxes
#         self.checkbox_rotation.setEnabled(False)
#         self.checkbox_elevation.setEnabled(False)
#         self.checkbox_buildingSelection.setEnabled(False)
#
#     def animButton(self,button):
#         self.animation = QPropertyAnimation(button, b"color", self)
#         self.animation.setDuration(1000)
#         self.animation.setLoopCount(100)
#         self.animation.setStartValue(button.default_color)
#         self.animation.setEndValue(button.default_color)
#         self.animation.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animation.start()
#
#     def animHelp1(self):
#         self.animationHelp1 = QPropertyAnimation(self.btn_help, b"color", self)
#         self.animationHelp1.setDuration(1000)
#         self.animationHelp1.setLoopCount(100)
#         self.animationHelp1.setStartValue(self.btn_help.default_color)
#         self.animationHelp1.setEndValue(self.btn_help.default_color)
#         self.animationHelp1.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animationHelp1.start()
#
#     def animHelp2(self):
#         self.animationHelp2 = QPropertyAnimation(self.btn_help2, b"color", self)
#         self.animationHelp2.setDuration(1000)
#         self.animationHelp2.setLoopCount(100)
#         self.animationHelp2.setStartValue(self.btn_help2.default_color)
#         self.animationHelp2.setEndValue(self.btn_help2.default_color)
#         self.animationHelp2.setKeyValueAt(0.1, QColor(255,20,20))
#         self.animationHelp2.start()
#
#
#     def checkRotation(self):
#         if self.checkbox_rotation.isChecked():
#             self.edit_rotation.setEnabled(True)
#         else:
#             self.edit_rotation.setText("0")
#             self.edit_rotation.setEnabled(False)
#
#     def checkElevation(self):
#         if self.checkbox_elevation.isChecked():
#             self.edit_elevation.setEnabled(True)
#         else:
#             self.edit_elevation.setText("0")
#             self.edit_elevation.setEnabled(False)
#
#
#     def selectAllBuildings(self):
#         self.buildingList = readCityGML(self.inputFileName,self.mainWindow._nameSpace)
#         # set up search List
#         for building in self.buildingList:
#             self.buildingSelectionList.append(str(building.name).split("'")[-2])
#
#     def onToggleBuildingSelection(self):
#         if self.checkbox_buildingSelection.isChecked():
#             self.buildingSelectionList = []
#             self.lbl_manual_setting_number.\
#                 setText("Number of Buildings Selected = "+str(len(self.buildingSelectionList)))
#
#             self.btn_buildingSelection.setEnabled(True)
#             self.checkbox_rotation.setChecked(True)
#             self.checkbox_elevation.setChecked(True)
#         else:
#             self.selectAllBuildings()
#             self.lbl_manual_setting_number.setText("Number of Buildings Selected = ALL")
#             # disable
#             self.btn_buildingSelection.setEnabled(False)
#             self.checkbox_rotation.setChecked(False)
#             self.checkbox_elevation.setChecked(False)
#         return 0
#
#     def openBuildingListWindow(self):
#         # open a BuildingListWindow
#         self.buildingListWindow = BuildingListWindow()
#         self.buildingListWindow.mainWindow = self
#         self.buildingListWindow.resize(300,300)
#
#         self.buildingList = readCityGML(self.inputFileName,self.mainWindow._nameSpace)
#         # set up search List
#         for building in self.buildingList:
#             self.buildingListWindow.buildingNameList.append(str(building.name).split("'")[-2])
#
#         self.buildingListWindow.buildingQueue.setStringList(self.buildingListWindow.buildingNameList)
#         self.buildingListWindow.searchCompleter = QCompleter()
#         self.buildingListWindow.searchCompleter.setModel(self.buildingListWindow.buildingQueue)
#         self.buildingListWindow.searchBar.setCompleter(self.buildingListWindow.searchCompleter)
#
#         for item in self.buildingSelectionList:
#             self.buildingListWindow.lst_building.addItem(item)
#
#         # theme
#         if self.mainWindow.theme == "Light":
#             '''
#             #dark blue
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240)}
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240)}
#                 QLabel{color:rgb(39, 39, 39)}""")
#             self.buildingListWindow.lst_building.setStyleSheet("""QListWidget{background-color:rgb(240,240,240)}
#                         QListWidget::Item:hover{background:skyblue; }
#                         QListWidget::item:selected:!active{border-width:0px; background:lightgreen;}""")
#         else:
#             self.buildingListWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30)}
#                 QLabel{color:rgb(238, 248, 255)}""")
#             self.buildingListWindow.lst_building.setStyleSheet("""QListWidget{background-color:rgb(130,145,150)}
#                         QListWidget::Item:hover{background:skyblue; }
#                         QListWidget::item:selected:!active{border-width:0px; background:lightgreen;}""")
#
#         self.buildingListWindow.show()
#         self.hide()
#
#     def openInfoWindow(self):
#         # stop animation
#         try:
#             self.animationHelp1.stop()
#             self.btn_help.reset_color()
#         except:
#             pass
#
#         self.infoWindow = InfoWindow(self)
#
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.infoWindow.resize(300, 350)
#         else:
#             # for 4k high-resolution
#             self.infoWindow.resize(600, 700)
#
#         if self.mainWindow.theme == "Light":
#             '''
#             #dark blue
#             self.infoWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark blue
#             self.infoWindow.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}""")
#         else:
#             self.infoWindow.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}""")
#
#         self.infoWindow.show()
#         self.infoWindow.mainWindow = self
#
#
#     def openInfoWindowE(self):
#         # stop animation
#         try:
#             self.animationHelp2.stop()
#             self.btn_help2.reset_color()
#         except:
#             pass
#
#         self.infoWindowE = InfoWindowE(self)
#
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.infoWindowE.resize(300, 350)
#         else:
#             # for 4k high-resolution
#             self.infoWindowE.resize(600, 700)
#
#         if self.mainWindow.theme == "Light":
#             '''
#             #dark blue
#             self.infoWindowE.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(35, 46, 130)}""")
#             '''
#             #dark grey
#             self.infoWindowE.setStyleSheet("""QDialog{background-color:rgb(255, 250, 240);}\
#                 QLabel{color:rgb(39, 39, 39)}""")
#         else:
#             self.infoWindowE.setStyleSheet("""QDialog{background-color:rgb(20, 25, 30);}\
#                 QLabel{color:rgb(238, 248, 255)}""")
#
#         self.infoWindowE.show()
#         self.infoWindowE.mainWindow = self
#
#     def transformLonLat(self):
#         try:
#             lon = float(self.edit_lon.text())
#             lat = float(self.edit_lat.text())
#         except:
#             self.msgBoxCreator("Please enter valid number!")
#             return 1
#
#         wgs = CRS("EPSG:4326")
#         OutProj = CRS(self.cmb_output_crs.currentText().split(" ")[0])
#
#         try:
#             x,y = transform(wgs,OutProj,lat,lon)
#
#             self.edit_targetPoint_x.setText(str(x))
#             self.edit_targetPoint_y.setText(str(y))
#             self.edit_targetPoint_z.setText("0")
#
#             # stop animation
#             self.animation.stop()
#             self.btn_lonlat.reset_color()
#             self.animHelp1()
#             self.animHelp2()
#         except:
#             self.msgBoxCreator("CRS error")
#             return 1
#
#         # Initialize the selectionReference,
#         # by default all buildings will be selected for rotation/elevation transformation
#         self.selectAllBuildings()
#         # enable check boxes
#         self.checkbox_rotation.setEnabled(True)
#         self.checkbox_elevation.setEnabled(True)
#         self.checkbox_buildingSelection.setEnabled(True)
#
#     def updateProgressBar(self):
#         self.progressBar.setValue(len(self.workerThread.buildingResult))
#
#     def transformationCompleted(self,executionTime):
#         self.btn_transform_xml.setEnabled(True)
#         self.btn_exit_transformation.setEnabled(True)
#
#         time_str = str(executionTime)[0:6]
#         self.msgBoxCreator("Transformation Completed in "+time_str+" Seconds.")
#
#         #enable the output button in VisualizationWindow.
#         self.mainWindow.isTransformed=True
#
#     def transformXML(self):
#         start_time = time.time()
#
#         # target location: values are in target CRS. and this is a location in London:
#         tp_x = 0
#         tp_y = 0
#         tp_z = 0
#         #Angle & Elevation
#         angle = 0
#         elevationChange = 0
#         try:
#             tp_x = float(self.edit_targetPoint_x.text())
#             tp_y = float(self.edit_targetPoint_y.text())
#             tp_z = float(self.edit_targetPoint_z.text())
#             angle = float(self.edit_rotation.text())
#             elevationChange = float(self.edit_elevation.text())
#         except:
#             self.msgBoxCreator("Please Transform the LatLon to XYZ-coordinates.")
#             return 1
#
#         targetLoc = [tp_x,tp_y,tp_z]
#
#         # start to transform
#         fileName = self.inputFileName
#         fileName_exported = self.outputFileName
#         if fileName=="" or fileName_exported=="":
#             print("Files are not ready.")
#             return 1
#
#         # in&out projected CRS, format: "epsg:xxxx"
#         inputCRS_str = self.cmb_input_crs.currentText()
#         outputCRS_str = self.cmb_output_crs.currentText()
#         inputCRS_str = inputCRS_str.split(" ")[0]
#         outputCRS_str = outputCRS_str.split(" ")[0]
#
#         inProj = Proj(inputCRS_str)
#         outProj = Proj(outputCRS_str)
#
#         # check if the target point is in the range of the output_CRS
#         # get the CRS for output
#         print("outputCRS = ",outputCRS_str.split(':')[-1])
#         outputCRS = CRS.from_epsg(int(outputCRS_str.split(':')[-1]))
#         print("outputCRS.area_of_use (W,S,E,N)",outputCRS.area_of_use.west,', ',\
#             outputCRS.area_of_use.south,', ',outputCRS.area_of_use.east,', ',\
#             outputCRS.area_of_use.north)
#
#         # the boundary of output CRS is presented by two corners, (west,south) and (east,north)
#         # project these two points from degree to meter:
#         # "outProj(west,south)" gives the bottom-left corner in the unit of meter.
#
#         x_west,y_south = outProj(outputCRS.area_of_use.west,outputCRS.area_of_use.south)
#         x_east,y_north = outProj(outputCRS.area_of_use.east,outputCRS.area_of_use.north)
#
#         # now check if our target point is within the boundary of outputCRS
#         if (tp_x >= x_west and tp_x <= x_east) and (tp_y >= y_south and tp_y <= y_north):
#             print("Target point falls within the boundary of outProj.")
#         else:
#             self.msgBoxCreator(\
#                 "Target point [x,y,z] out of the projected bounds of the output CRS.\nPlease re-enter tartget point or choose other output CRS.")
#             return 1
#
#         print("========================================")
#
#
#         # save the xml data into buildingList. To call the building inside it,
#         # use buildingList[x].name or buildingList[x].roof (.foor or .wall)
#         self.buildingList = readCityGML(fileName,self.mainWindow._nameSpace)
#         print("Number buildings = ",len(self.buildingList))
#
#
#         # parse the xml file
#         tree = ET.parse(fileName)
#
#         # find the REF point and OFFSET vector.
#         pt_REF = getREF(tree.getroot(),self.mainWindow._nameSpace,inProj,outProj)
#         OFFSET = np.subtract(np.array(targetLoc),np.array(pt_REF))
#         OFFSET[2] = 0
#
#          # establish QThread
#         self.workerThread = WorkerThread()
#         self.workerThread.finished.connect(self.transformationCompleted)
#
#         self.workerThread.buildingList = self.buildingList
#         self.workerThread.OFFSET = OFFSET
#         self.workerThread.inputCRS = inputCRS_str
#         self.workerThread.outputCRS = outputCRS_str
#         self.workerThread.angle = angle
#         self.workerThread.elevationChange = elevationChange
#         self.workerThread.fileName_input = fileName
#         self.workerThread.fileName_exported = fileName_exported
#         self.workerThread.selectionReference = self.buildingSelectionList
#         self.workerThread._nameSpace = self.mainWindow._nameSpace
#
#         # make progressBar alive
#         self.progressBar.setRange(0,len(self.buildingList))
#         self.progressBar.setValue(0)
#
#         timer = QTimer(self)
#         timer.timeout.connect(self.updateProgressBar)
#         timer.start(100)
#
#         #disable "start" button once the thread begins
#         self.btn_transform_xml.setEnabled(False)
#         self.workerThread.start()
#
#         # see function transformationCompleted(self) for what will happen once the jone done.
#         # after successful transformation, animate "visualization" and "validation" button
#         self.mainWindow.animVisualization()
#         self.mainWindow.animValidation()
#         return 0
#
#     # create a QMessageBox when needed
#     def msgBoxCreator(self,text):
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText(text)
#         self.msg.show()
#
#     def close_window(self):
#         # back to mainWindow and close the sub-window.
#         self.mainWindow.show()
#         self.close()
#         return 0
# # **********************************************************************************
# class InfoWindow(QDialog):
#     def __init__(self, parent=None):
#         super(InfoWindow, self).__init__(parent)
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.mainWindow =_TransformationWindow()
#         self.setWindowTitle('Help for Rotation Setting')
#
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         self.vbox_info = QVBoxLayout()
#         self.setLayout(self.vbox_info)
#
#         self.gbox_info = QGroupBox()
#         self.vbox_intro = QVBoxLayout()
#         self.gbox_info.setLayout(self.vbox_intro)
#         self.vbox_info.addWidget(self.gbox_info)
#
#         self.lbl_info = QLabel("A positive angle will rotate buildings \nin counterclockwise order\nA negative value for clockwise rotation")
#         self.lbl_info.setFont(self.myBoldFont)
#         self.vbox_intro.addWidget(self.lbl_info)
#
#         self.lbl_intro = QLabel(self)
#         self.picIntro = QPixmap("InfoRotation.png")
#         self.picIntro = self.picIntro.scaled(400,300,Qt.KeepAspectRatio)
#         self.lbl_intro.setPixmap(self.picIntro)
#         self.vbox_intro.addWidget(self.lbl_intro)
#
#         self.btn_exit_info = QPushButton("Back")
#         self.btn_exit_info.setFont(self.myBoldFont)
#         self.btn_exit_info.clicked.connect(self.close_window)
#         self.btn_exit_info.setStyleSheet("font:bold;background-color:rgb(174, 163, 163);font-weight:bold")
#         self.vbox_info.addWidget(self.btn_exit_info)
#
#     def close_window(self):
#         #self.mainWindow.show()
#         self.close()
#         return 0
# #**********************************************************************************
# class InfoWindowE(QDialog):
#     def __init__(self, parent=None):
#         super(InfoWindowE, self).__init__(parent)
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.mainWindow =_TransformationWindow()
#         self.setWindowTitle('Help for Elevation Setting')
#
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         self.vbox_info = QVBoxLayout()
#         self.setLayout(self.vbox_info)
#
#         self.gbox_info = QGroupBox()
#         self.vbox_intro = QVBoxLayout()
#         self.gbox_info.setLayout(self.vbox_intro)
#         self.vbox_info.addWidget(self.gbox_info)
#
#         self.lbl_info = QLabel("The orginal elevation is from the Z-axis value in the GML file.\nWhat you add here is elevation change")
#         self.lbl_info.setFont(self.myBoldFont)
#         self.vbox_intro.addWidget(self.lbl_info)
#
#         self.lbl_intro = QLabel(self)
#         self.picIntro = QPixmap("InfoElevation.png")
#         self.picIntro = self.picIntro.scaled(400,300,Qt.KeepAspectRatio)
#         self.lbl_intro.setPixmap(self.picIntro)
#         self.vbox_intro.addWidget(self.lbl_intro)
#
#         self.btn_exit_info = QPushButton("Back")
#         self.btn_exit_info.setFont(self.myBoldFont)
#         self.btn_exit_info.clicked.connect(self.close_window)
#         self.btn_exit_info.setStyleSheet("font:bold;background-color:rgb(174, 163, 163);font-weight:bold")
#         self.vbox_info.addWidget(self.btn_exit_info)
#
#     def close_window(self):
#         #self.mainWindow.show()
#         self.close()
#         return 0
# #**********************************************************************************
#
# # class for figure Pan and Zoom,
# # Ref: https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
# class PhotoViewer(QGraphicsView):
#     photoClicked = pyqtSignal(QPoint)
#
#     def __init__(self, parent):
#         super(PhotoViewer, self).__init__(parent)
#         self._zoom = 0
#         self._empty = True
#         self._scene = QGraphicsScene(self)
#         self._photo = QGraphicsPixmapItem()
#         self._scene.addItem(self._photo)
#         self.setScene(self._scene)
#         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setBackgroundBrush(QBrush(QColor(200, 200, 200)))
#         self.setFrameShape(QFrame.NoFrame)
#
#     def hasPhoto(self):
#         return not self._empty
#
#     def fitInView(self, scale=True):
#         rect = QRectF(self._photo.pixmap().rect())
#         if not rect.isNull():
#             self.setSceneRect(rect)
#             if self.hasPhoto():
#                 unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
#                 self.scale(1 / unity.width(), 1 / unity.height())
#                 viewrect = self.viewport().rect()
#                 scenerect = self.transform().mapRect(rect)
#                 factor = min(viewrect.width() / scenerect.width(),
#                              viewrect.height() / scenerect.height())
#                 self.scale(factor, factor)
#             self._zoom = 0
#
#     def setPhoto(self, pixmap=None):
#         self._zoom = 0
#         if pixmap and not pixmap.isNull():
#             self._empty = False
#             self.setDragMode(QGraphicsView.ScrollHandDrag)
#             self._photo.setPixmap(pixmap)
#         else:
#             self._empty = True
#             self.setDragMode(QGraphicsView.NoDrag)
#             self._photo.setPixmap(QPixmap())
#         self.fitInView()
#
#     def wheelEvent(self, event):
#         if self.hasPhoto():
#             if event.angleDelta().y() > 0:
#                 factor = 1.25
#                 self._zoom += 1
#             else:
#                 factor = 0.8
#                 self._zoom -= 1
#             if self._zoom > 0:
#                 self.scale(factor, factor)
#             elif self._zoom == 0:
#                 self.fitInView()
#             else:
#                 self._zoom = 0
#
#     def toggleDragMode(self):
#         if self.dragMode() == QGraphicsView.ScrollHandDrag:
#             self.setDragMode(QGraphicsView.NoDrag)
#         elif not self._photo.pixmap().isNull():
#             self.setDragMode(QGraphicsView.ScrollHandDrag)
#
#     def mousePressEvent(self, event):
#         if self._photo.isUnderMouse():
#             self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
#         super(PhotoViewer, self).mousePressEvent(event)
#
# class _DrawWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_DrawWindow, self).__init__(parent)
#
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle('Building Visualization')
#         # save the mainWindow
#         self.mainWindow = _MainWindow()
#
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#
#         # file names for drawings
#         self.inputFileName = ""
#         self.outputFileName = ""
#         # set up figure's DPI
#         self.myDPI = 500
#
#
#         # base-layout
#         self.vbox_show_fig = QVBoxLayout()
#         self.setLayout(self.vbox_show_fig)
#
#         self.inandoutLayout = QHBoxLayout()
#         self.vbox_show_fig.addLayout(self.inandoutLayout)
#
#         # TWO sub-layouts, figures for input_xml and output_xml
#         # figure of input_xml
#         self.gbox_input_fig = QGroupBox()
#         self.vbox_input_fig = QVBoxLayout()
#         self.gbox_input_fig.setLayout(self.vbox_input_fig)
#
#         self.btn_input_fig = QPushButton('Visualization Input',self)
#         self.btn_input_fig.clicked.connect(lambda: self.show_fig("input"))
#         self.btn_input_fig.setFont(self.myBoldFont)
#         self.btn_input_fig.setStyleSheet("background-color:rgb(238, 248, 255);font-weight:bold")
#         self.vbox_input_fig.addWidget(self.btn_input_fig)
#
#         self.viewer_in = PhotoViewer(self)
#         self.vbox_input_fig.addWidget(self.viewer_in)
#
#         self.inandoutLayout.addWidget(self.gbox_input_fig)
#
#         # figure of outfut_xml
#         self.gbox_output_fig = QGroupBox()
#         self.vbox_output_fig = QVBoxLayout()
#         self.gbox_output_fig.setLayout(self.vbox_output_fig)
#
#         self.btn_output_fig = QPushButton('Visualization Output',self)
#         if self.mainWindow.isTransformed:
#             self.btn_output_fig.setEnabled(True)
#         else:
#             self.btn_output_fig.setEnabled(True)
#         self.btn_output_fig.clicked.connect(lambda: self.show_fig("output"))
#         self.btn_output_fig.setFont(self.myBoldFont)
#         self.btn_output_fig.setStyleSheet("background-color:rgb(238, 248, 255);font-weight:bold")
#         self.vbox_output_fig.addWidget(self.btn_output_fig)
#
#         self.viewer_out = PhotoViewer(self)
#         self.vbox_output_fig.addWidget(self.viewer_out)
#
#         self.inandoutLayout.addWidget(self.gbox_output_fig)
#
#         # add a button to exit this drawWindow()
#         self.btn_exit_drawWindow = QPushButton("Back",self)
#         self.btn_exit_drawWindow.clicked.connect(self.close_window)
#         self.btn_exit_drawWindow.setStyleSheet("background-color:rgb(174, 163, 163);font-weight:bold")
#         self.btn_exit_drawWindow.setFont(self.myBoldFont)
#         self.vbox_show_fig.addWidget(self.btn_exit_drawWindow)
#         #------------------------------------------------------------------------
#
#     def drawingCompleted(self,signal):
#         # this signal argument is to indicate whether the result is for inputXML or outputXML
#
#         self.resize(1600,800)
#         self.show()
#
#         if signal:
#             self.btn_input_fig.setEnabled(True)
#             self.viewer_in.setPhoto(QPixmap(self.drawingThread_in.fileName_png))
#         else:
#             self.btn_output_fig.setEnabled(True)
#             self.viewer_out.setPhoto(QPixmap(self.drawingThread_out.fileName_png))
#
#         self.msgBoxCreator("Transformation completed successfully\nExport .png file to the working directory of your New folder")
#         #stop animation
#         try:
#             self.mainWindow.animationVis.stop()
#             self.mainWindow.btn_draw_xml.reset_color()
#         except:
#             # clicked before transformation
#             return -1
#
#     def show_fig(self,inputOrOutput):
#         if inputOrOutput == "input":
#             self.btn_input_fig.setEnabled(False)
#             self.drawingThread_in = DrawingThread()
#             self.drawingThread_in.finished.connect(self.drawingCompleted)
#
#             self.drawingThread_in.fileName_xml = self.inputFileName
#             self.drawingThread_in.fileName_png = self.mainWindow.folder_name+"/Visualization_InputCityGML.png"
#             self.drawingThread_in.myDPI = self.myDPI
#             self.drawingThread_in.isInput = True
#
#             self.drawingThread_in.start()
#         else:
#             self.btn_output_fig.setEnabled(False)
#             self.drawingThread_out = DrawingThread()
#             self.drawingThread_out.finished.connect(self.drawingCompleted)
#             self.drawingThread_out.fileName_xml = self.outputFileName
#             self.drawingThread_out.fileName_png = self.mainWindow.folder_name+"/Visualization_TransformedCityGML.png"
#             self.drawingThread_out.myDPI = self.myDPI
#             self.drawingThread_out.isInput = False
#
#             self.drawingThread_out.start()
#
#
#     def msgBoxCreator(self,text):
#         self.msg = QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         if self.mainWindow.theme == "Light":
#             '''
#             #dark blue
#             self.msg.setStyleSheet("""QLabel{color:rgb(35, 46, 130)}
#                     QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#             '''
#             #dark blue
#             self.msg.setStyleSheet("""QLabel{color:rgb(39, 39, 39)}
#                     QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#         else:
#             self.msg.setStyleSheet("""QLabel{color:rgb(238, 248, 255)}
#                     QPushButton{background-color:rgb(180,180,180);font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText(text)
#         self.msg.show()
#
#     def close_window(self):
#         self.mainWindow.show()
#         self.close()
#         return 0
# # **********************************************************************************
#
# class _ValidationWindow(QDialog):
#     def __init__(self,parent=None):
#         super(_ValidationWindow, self).__init__(parent)
#
#         self.setWindowIcon(QIcon('e3dIcon.png'))
#         self.setWindowTitle('CityGML Validation')
#         # save the mainWindow
#         self.mainWindow = _MainWindow()
#         # Font Settings
#         self.myBoldFont = QFont()
#         self.myBoldFont.setFamily("Arial")
#         self.myBoldFont.setBold(True)
#         self.mySlimFont = QFont()
#         self.mySlimFont.setFamily("Arial")
#         self.mySlimFont.setBold(False)
#         try:
#             screenWidth = GetSystemMetrics(0)
#             screenHeight =  GetSystemMetrics(1)
#         except:
#             screenWidth = 1920
#             screenHeight = 1080
#
#         if screenWidth <= 2400 or screenHeight <= 1200:
#             self.myBoldFont.setPointSize(9)
#             self.mySlimFont.setPointSize(9)
#         else:
#             # for 4k high-resolution
#             self.myBoldFont.setPointSize(18)
#             self.mySlimFont.setPointSize(18)
#         # file names for validation
#         self.inputFileName = ""
#         self.outputFileName = ""
#         self.report_str = ""
#         # base-layout, which contains ONE hbox, and a button to close the window.
#         self.vbox_validation = QVBoxLayout()
#         self.setLayout(self.vbox_validation)
#
#         # A horizontal layout contains TWO vertical layouts.
#         self.hbox_validation = QHBoxLayout()
#         self.vbox_validation.addLayout(self.hbox_validation)
#         # add a close button
#         self.btn_exit_validationWindow = QPushButton("Back")
#         self.btn_exit_validationWindow.clicked.connect(self.close_window)
#         self.btn_exit_validationWindow.setFont(self.myBoldFont)
#         self.btn_exit_validationWindow.setStyleSheet("background-color:rgb(174, 163, 163);font-weight:bold")
#         self.vbox_validation.addWidget(self.btn_exit_validationWindow)
#
#         # Now design the hbox_validation
#         self.vbox_validation_input = QVBoxLayout()
#         #self.vbox_validation_input.setAlignment(Qt.AlignCenter)
#         self.hbox_validation.addLayout(self.vbox_validation_input)
#         self.vbox_validation_output = QVBoxLayout()
#         #self.vbox_validation_output.setAlignment(Qt.AlignCenter)
#         self.hbox_validation.addLayout(self.vbox_validation_output)
#         #------------------------------------------------------------------------
#
#          # Module: validation, Input XML
#         self.btn_validation_input = QPushButton("Validatate Input XML",self)
#         self.btn_validation_input.setFont(self.myBoldFont)
#         self.btn_validation_input.setStyleSheet("background-color:rgb(238, 248, 255);font-weight:bold")
#         self.vbox_validation_input.addWidget(self.btn_validation_input)
#         #the button clicked connect will be state later
#
#         # layout for results: ONE hbox contains TWO vboxes.
#         self.gbox_invalid_result_input = QGroupBox()
#         self.hbox_invalid_result_input = QHBoxLayout()
#         self.gbox_invalid_result_input.setLayout(self.hbox_invalid_result_input)
#
#         self.vbox_invalid_question_input = QVBoxLayout()
#         self.vbox_invalid_answer_input =QVBoxLayout()
#         # create widgets for questions and answers, e.g., how many invalid buildings, or total number
#         # of buildings?
#         self.lbl_num_of_buildings_input = QLabel("NO. of Buildings in Total: ",self)
#         self.lbl_num_of_buildings_input.setFont(self.mySlimFont)
#         self.vbox_invalid_question_input.addWidget(self.lbl_num_of_buildings_input)
#         self.lbl_num_of_invalid_bldg_input = QLabel("NO. of Buildings Invalid: ",self)
#         self.lbl_num_of_invalid_bldg_input.setFont(self.mySlimFont)
#         self.vbox_invalid_question_input.addWidget(self.lbl_num_of_invalid_bldg_input)
#         self.lbl_num_of_invalid_polygon_input = QLabel("NO. of Invalid Polygons: ",self)
#         self.lbl_num_of_invalid_polygon_input.setFont(self.mySlimFont)
#         self.vbox_invalid_question_input.addWidget(self.lbl_num_of_invalid_polygon_input)
#         # Answers to the Questions
#         self.lbl_val_num_of_buildings_input = QLabel("x",self)
#         self.lbl_val_num_of_buildings_input.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_input.addWidget(self.lbl_val_num_of_buildings_input)
#         self.lbl_val_num_of_invalid_bldg_input = QLabel("x",self)
#         self.lbl_val_num_of_invalid_bldg_input.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_input.addWidget(self.lbl_val_num_of_invalid_bldg_input)
#         self.lbl_val_num_of_invalid_polygon_input = QLabel("x",self)
#         self.lbl_val_num_of_invalid_polygon_input.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_input.addWidget(self.lbl_val_num_of_invalid_polygon_input)
#
#         self.hbox_invalid_result_input.addLayout(self.vbox_invalid_question_input)
#         self.hbox_invalid_result_input.addLayout(self.vbox_invalid_answer_input)
#         self.vbox_validation_input.addWidget(self.gbox_invalid_result_input)
#
#         # Button to Save details in the txt file.
#         self.btn_validation_save_input = QPushButton("Save as A Validation Report",self)
#         self.btn_validation_save_input.setStyleSheet("background-color:rgb(180,180,180);color:black")
#         self.btn_validation_save_input.setFont(self.myBoldFont)
#         self.btn_validation_save_input.setEnabled(False)
#         self.btn_validation_save_input.clicked.connect(lambda: self.saveReport("input"))
#         self.vbox_validation_input.addWidget(self.btn_validation_save_input)
#
#         #------------------------------------------------------------------------
#
#         # Module: validation, Output XML, almost the same
#         self.btn_validation_output = QPushButton("Validate Output XML",self)
#         self.btn_validation_output.setFont(self.myBoldFont)
#         self.btn_validation_output.setStyleSheet("background-color:rgb(238, 248, 255);font-weight:bold")
#         self.vbox_validation_output.addWidget(self.btn_validation_output)
#         #the button clicked connect will be state later
#
#         # layout for results
#         self.gbox_invalid_result_output = QGroupBox()
#         self.hbox_invalid_result_output = QHBoxLayout()
#         self.gbox_invalid_result_output.setLayout(self.hbox_invalid_result_output)
#
#         self.vbox_invalid_question_output = QVBoxLayout()
#         self.vbox_invalid_answer_output =QVBoxLayout()
#         # Questions:
#         self.lbl_num_of_buildings_output = QLabel("NO. of Buildings in Total: ",self)
#         self.lbl_num_of_buildings_output.setFont(self.mySlimFont)
#         self.vbox_invalid_question_output.addWidget(self.lbl_num_of_buildings_output)
#         self.lbl_num_of_invalid_bldg_output = QLabel("NO. of Buildings Invalid: ",self)
#         self.lbl_num_of_invalid_bldg_output.setFont(self.mySlimFont)
#         self.vbox_invalid_question_output.addWidget(self.lbl_num_of_invalid_bldg_output)
#         self.lbl_num_of_invalid_polygon_output = QLabel("NO. of Invalid Polygons: ",self)
#         self.lbl_num_of_invalid_polygon_output.setFont(self.mySlimFont)
#         self.vbox_invalid_question_output.addWidget(self.lbl_num_of_invalid_polygon_output)
#         # Answers:
#         self.lbl_val_num_of_buildings_output = QLabel("x",self)
#         self.lbl_val_num_of_buildings_output.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_output.addWidget(self.lbl_val_num_of_buildings_output)
#         self.lbl_val_num_of_invalid_bldg_output = QLabel("x",self)
#         self.lbl_val_num_of_invalid_bldg_output.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_output.addWidget(self.lbl_val_num_of_invalid_bldg_output)
#         self.lbl_val_num_of_invalid_polygon_output = QLabel("x",self)
#         self.lbl_val_num_of_invalid_polygon_output.setFont(self.mySlimFont)
#         self.vbox_invalid_answer_output.addWidget(self.lbl_val_num_of_invalid_polygon_output)
#
#         self.hbox_invalid_result_output.addLayout(self.vbox_invalid_question_output)
#         self.hbox_invalid_result_output.addLayout(self.vbox_invalid_answer_output)
#         self.vbox_validation_output.addWidget(self.gbox_invalid_result_output)
#
#         # Save details in the txt file. While it is disabled, it shows in gray (Blue for activeated).
#         self.btn_validation_save_output = QPushButton("Save as A Validation Report",self)
#         self.btn_validation_save_output.setStyleSheet("background-color:rgb(180,180,180);color:black")
#         self.btn_validation_save_output.setFont(self.myBoldFont)
#         self.btn_validation_save_output.setEnabled(False)
#         self.btn_validation_save_output.clicked.connect(lambda: self.saveReport("output"))
#         self.vbox_validation_output.addWidget(self.btn_validation_save_output)
#         #------------------------------------------------------------------------
#         # add clicked function to buttons
#         self.btn_validation_input.clicked.connect(lambda: self.validation_xml("input"))
#         self.btn_validation_output.clicked.connect(lambda: self.validation_xml("output"))
#
#     def validationCompleted(self, signal):
#         # About signal
#         executionTime = signal[0]
#         isInputOrOutput = signal[1]
#
#         self.report_str = ""
#         num_invalid_geometry = 0
#         num_invalid_building = 0
#
#         if isInputOrOutput:
#             buildingResult = self.validationThread_in.buildingResult
#             self.btn_validation_input.setEnabled(True)
#         else:
#             buildingResult = self.validationThread_out.buildingResult
#             self.btn_validation_output.setEnabled(True)
#
#         for i in range(len(buildingResult)):
#             invalidOne = buildingResult[i]
#             if invalidOne.cmt == "Valid":
#                 continue
#             else:
#                 num_invalid_building += 1
#                 for roof in invalidOne.roof:
#                     if roof.cmt != "Valid":
#                         num_invalid_geometry += 1
#                         newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
#                         ";\n\n Roof Issue = "+str(roof.name)+"\n\n"+str(roof.cmt)+\
#                         "------------------------------------------------------------------------\n\n"
#                         #print("Building No ",i,">>",newInvalidStr)
#                         self.report_str += newInvalidStr
#                 for foot in invalidOne.foot:
#                     if foot.cmt != "Valid":
#                         num_invalid_geometry += 1
#                         newInvalidStr = str(num_invalid_geometry)+". In This Building = "\
#                         +str(invalidOne.name)+\
#                         ";\n\n Foot Issue = "+str(foot.name)+"\n\n"+str(foot.cmt)+\
#                         "------------------------------------------------------------------------\n\n"
#                         #print("Building No ",i,">>",newInvalidStr)
#                         self.report_str += newInvalidStr
#                 for wall in invalidOne.wall:
#                     if wall.cmt != "Valid":
#                         num_invalid_geometry += 1
#                         newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
#                         ";\n\n Wall Issue = "+str(wall.name)+"\n\n"+str(wall.cmt)+\
#                         "------------------------------------------------------------------------\n\n"
#                         #print("Building No ",i,">>",newInvalidStr)
#                         self.report_str += newInvalidStr
#
#         if isInputOrOutput == "input":
#             print("number of invalid LinearRings = ",num_invalid_geometry)
#             self.lbl_val_num_of_invalid_polygon_input.setText(str(num_invalid_geometry))
#             print("cpu_count = ",mp.cpu_count())
#             print("number of invalid Buildings = ",num_invalid_building,"/",len(buildingResult))
#             self.lbl_val_num_of_buildings_input.setText(str(len(buildingResult)))
#             self.lbl_val_num_of_invalid_bldg_input.setText(str(num_invalid_building))
#         else:
#             print("number of invalid LinearRings = ",num_invalid_geometry)
#             self.lbl_val_num_of_invalid_polygon_output.setText(str(num_invalid_geometry))
#             print("cpu_count = ",mp.cpu_count())
#             print("number of invalid Buildings = ",num_invalid_building,"/",len(buildingResult))
#             self.lbl_val_num_of_buildings_output.setText(str(len(buildingResult)))
#             self.lbl_val_num_of_invalid_bldg_output.setText(str(num_invalid_building))
#
#         if num_invalid_building == 0:
#             self.report_str = "All buildings are valid!"
#             self.msg= QMessageBox(self)
#             self.msg.setFont(self.myBoldFont)
#             self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#             self.msg.\
#             setText("All buildings are valid!\nValidation Completed in "+str(executionTime)[0:6]+" Seconds.")
#             self.msg.show()
#         else:
#             self.report_str += "\n Number of invalid LinearRings = "+str(num_invalid_geometry)+"\n"
#             self.report_str += "\n Number of invalid Buildings = "\
#             +str(num_invalid_building)+"/"+str(len(buildingResult))+"\n"
#
#             self.msg= QMessageBox(self)
#             self.msg.setFont(self.myBoldFont)
#             self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#             self.msg.setText("Validation Completed in "+str(executionTime)[0:6]+" Seconds.")
#             self.msg.show()
#
#         #stop animation
#         try:
#             self.mainWindow.animationVal.stop()
#             self.mainWindow.btn_validate_xml.reset_color()
#         except:
#             return -1
#
#     def validation_xml(self,inputOrOutput):
#         start_time = time.time()
#
#         if inputOrOutput == "input":
#             fileName = self.inputFileName
#             self.btn_validation_input.setEnabled(False)
#         else:
#             fileName = self.outputFileName
#             self.btn_validation_output.setEnabled(False)
#
#
#         # save the xml data into buildingList. To call the building inside it,
#         # use buildingList[x].name or buildingList[x].roof (.foor or .wall)
#         try:
#             buildingList = v_readCityGML(fileName,self.mainWindow._nameSpace)
#             print("Number buildings = ",len(buildingList))
#         except:
#             print("File does not exist")
#             if inputOrOutput == "input":
#                 self.btn_validation_input.setEnabled(True)
#             else:
#                 self.btn_validation_output.setEnabled(True)
#             return -1
#
#         #------------------------------------------------------
#
#         if inputOrOutput == "input":
#             self.btn_validation_save_input.setEnabled(True)
#             self.btn_validation_save_input.setStyleSheet("background-color:rgb(135,206,250);color:black")
#             self.btn_validation_save_output.setEnabled(False)
#             self.btn_validation_save_output.setStyleSheet("background-color:rgb(180,180,180);color:black")
#             # prepare for multiprocessing
#
#             self.validationThread_in = ValidationThread()
#             self.validationThread_in.buildingList = buildingList
#             self.validationThread_in.isInput = True
#
#             self.validationThread_in.finished.connect(self.validationCompleted)
#             self.validationThread_in.start()
#
#         else:
#             self.btn_validation_save_input.setEnabled(False)
#             self.btn_validation_save_input.setStyleSheet("background-color:rgb(180,180,180);color:black")
#             self.btn_validation_save_output.setEnabled(True)
#             self.btn_validation_save_output.setStyleSheet("background-color:rgb(135,206,250);color:black")
#             # prepare for multiprocessing
#
#             self.validationThread_out = ValidationThread()
#             self.validationThread_out.buildingList = buildingList
#             self.validationThread_out.isInput = False
#
#             self.validationThread_out.finished.connect(self.validationCompleted)
#             self.validationThread_out.start()
#
#
#
#     def saveReport(self,inputOrOutput):
#         if inputOrOutput == "input":
#             self.fileNameReport_input = self.mainWindow.folder_name+"/Validation_report_for_inputGML.txt"
#             with open(self.fileNameReport_input,'w') as f_handle:
#                 f_handle.write(self.report_str)
#         else:
#             self.fileNameReport_output = self.mainWindow.folder_name+"/Validation_report_for_outputGML.txt"
#             with open(self.fileNameReport_output,'w') as f_handle:
#                 f_handle.write(self.report_str)
#
#         self.msg= QMessageBox(self)
#         self.msg.setFont(self.myBoldFont)
#         self.msg.setStyleSheet("""QPushButton{background-color:rgb(180,180,180);\
#                                     font:9pt'Arial';font-weight:bold}""")
#         self.msg.setText("Validation Report Saved.")
#         self.msg.show()
#
#     def close_window(self):
#         self.mainWindow.show()
#         self.close()
#         return 0
# # **********************************************************************************

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet("QLabel{font-size: 8pt;} QPushButton{font-size: 8pt;} QRadioButton{font-size: 8pt;} QGroupBox{font-size: 8pt;} QComboBox{font-size: 8pt;} QLineEdit{font-size: 8pt;}")
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec_())