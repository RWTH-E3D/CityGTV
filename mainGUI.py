# import of libraries
import os
import sys
from PySide6 import QtWidgets, QtCore, QtGui
import pyproj
import time
import xml.etree.ElementTree as ET
import numpy as np
import multiprocessing as mp
import functools

import gui_fucntions as gf
import xmlParser_Process as xmlPP
import validation_Process as valP
import Just_Draw_gml as drawP

# positions and dimensions of window
POSX = 275
POSY = 100
WIDTH = 650
HEIGHT = 400
SIZEFACTOR = 0



class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self) -> None:
        """creates GUI for window"""
        
        global POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR
        POSX, POSY, WIDTH, HEIGHT, SIZEFACTOR = gf.screenSizer(POSX, POSY, WIDTH, HEIGHT, app)
        gf.windowSetup(self, POSX, POSY, WIDTH, HEIGHT, "CityGTV - MainWindow", SIZEFACTOR)

        # Setting main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        # Loading banner
        gf.load_banner(self, r'pictures/e3dHeaderGTV.png', SIZEFACTOR)

        self.tGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.tGrid)

        self.btn_select_input = QtWidgets.QPushButton("Select file")
        self.tGrid.addWidget(self.btn_select_input, 0, 0, 1, 1)
        self.btn_select_input.setFocus()

        self.txtB_input_file = QtWidgets.QLineEdit("")
        self.txtB_input_file.setEnabled(False)
        self.tGrid.addWidget(self.txtB_input_file, 0, 1, 1, 4)

        self.btn_select_output = QtWidgets.QPushButton("Select output folder")
        self.btn_select_output.setEnabled(False)
        self.tGrid.addWidget(self.btn_select_output, 1, 0, 1, 1)

        self.txtB_output_folder = QtWidgets.QLineEdit("")
        self.txtB_output_folder.setEnabled(False)
        self.tGrid.addWidget(self.txtB_output_folder, 1, 1, 1, 4)

        self.btn_transformation = QtWidgets.QPushButton("Transformation")
        self.btn_transformation.setEnabled(False)
        self.vbox.addWidget(self.btn_transformation)

        self.btn_visualisation = QtWidgets.QPushButton("Visualisation")
        self.btn_visualisation.setEnabled(False)
        self.vbox.addWidget(self.btn_visualisation)

        self.btn_validation = QtWidgets.QPushButton("Validation")
        self.btn_validation.setEnabled(False)
        self.vbox.addWidget(self.btn_validation)
        
        self.bGrid = QtWidgets.QGridLayout()
        self.vbox.addLayout(self.bGrid)

        self.btn_about = QtWidgets.QPushButton("About this tool")
        self.bGrid.addWidget(self.btn_about)

        self.btn_exit = QtWidgets.QPushButton("Exit")
        self.vbox.addWidget(self.btn_exit)
        self.btn_exit.clicked.connect(self.func_close)


        self.btn_select_input.clicked.connect(self.input_xml)
        self.btn_select_output.clicked.connect(self.func_select_folder)
        self.btn_transformation.clicked.connect(self.func_open_transformation)
        self.btn_visualisation.clicked.connect(self.func_open_visualisation)
        self.btn_validation.clicked.connect(self.func_open_validation)

        """some variables"""
        # for parsing XML files.
        # nameSpace used for ElementTree's search function
        self._nameSpace1 = {'core':"http://www.opengis.net/citygml/1.0",
        'gen':"http://www.opengis.net/citygml/generics/1.0",
        'grp':"http://www.opengis.net/citygml/cityobjectgroup/1.0",
        'app':"http://www.opengis.net/citygml/appearance/1.0",
        'bldg':"http://www.opengis.net/citygml/building/1.0",
        'gml':"http://www.opengis.net/gml",
        'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
        'xlink':"http://www.w3.org/1999/xlink",
        'xsi':"http://www.w3.org/2001/XMLSchema-instance"}

        # CityGML 2.0
        self._nameSpace2 = {'core':"http://www.opengis.net/citygml/2.0",
        'gen':"http://www.opengis.net/citygml/generics/2.0",
        'grp':"http://www.opengis.net/citygml/cityobjectgroup/2.0",
        'app':"http://www.opengis.net/citygml/appearance/2.0",
        'bldg':"http://www.opengis.net/citygml/building/2.0",
        'gml':"http://www.opengis.net/gml",
        'xal':"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
        'xlink':"http://www.w3.org/1999/xlink",
        'xsi':"http://www.w3.org/2001/XMLSchema-instance"}

        self.version = 0
        self.buildingList = []
        self.isTransformed = True
        self.filename_input = None


    def func_close(self) -> None:
        gf.close_application(self)


    def input_xml(self):
        tmp_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Input GML')[0]

        if os.path.isfile(tmp_path):
            try:
                # determine _nameSpace for XML parser
                with open(tmp_path,"r") as fileHandle:
                    for line in fileHandle.readlines():
                        #print("current line = ",line)
                        if str(line).find("citygml/1.0")!= -1:
                            self._nameSpace = self._nameSpace1
                            self.version = 1
                            print("CityGml Version = 1.0")
                            break
                        elif str(line).find("citygml/2.0")!= -1:
                            self._nameSpace = self._nameSpace2
                            self.version = 2
                            print("CityGML Version = 2.0")
                            break
                    # end loop 
                    if self.version == 0:
                        print("CityGML Version Not Supported.")
                        return -1
                #file closed
                self.filename_input = tmp_path
                self.txtB_input_file.setText(self.filename_input)

                self.buildingList = xmlPP.readCityGML(self.filename_input,self._nameSpace)
                tmp_text = 'InputGML File Information:  CityGML Version = '+str(self.version)+\
                '.0    Number of buildings = '+str(len(self.buildingList))

                self.setWindowTitle("CityGTV - " + tmp_text)                
                self.btn_select_output.setEnabled(True)
            except:
                gf.messageBox(self, "Error", "Unable to parse the file format")
                return 1
        else:
            pass
        return 0

    def func_select_folder(self):
        self.workingDirectory = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select export directory"))
        if self.workingDirectory:
            self.txtB_output_folder.setText(self.workingDirectory)
            self.btn_transformation.setEnabled(True)
            self.btn_validation.setEnabled(True)
            self.btn_visualisation.setEnabled(True)
        else:
            self.txtB_output_folder.setText('No Folder Selected')

    def func_open_transformation(self) -> None:
        """opens transformation window"""
        self.transformation = TransformationWindow(self)
        self.transformation.show()
        self.hide()

    def func_open_visualisation(self):
        """opens visualisation window"""
        self.visualisation = VisualisationWindow(self)
        self.visualisation.show()
        self.hide()

    def func_open_validation(self):
        """opens validation window"""
        self.validation = ValidationWindow(self)
        self.validation.show()
        self.hide()


class VisualisationWindow(QtWidgets.QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super(VisualisationWindow, self).__init__()
        self.parent = parent
        self.input_file = self.parent.filename_input
        self.output_file = self.parent.workingDirectory + "/Transformation_Result.gml"
        self.initUI()

    def initUI(self):
        gf.windowSetup(self, POSX +100, POSY +100, WIDTH + (300*SIZEFACTOR), HEIGHT + (100*SIZEFACTOR), "CityGTV - Building Visualisation", SIZEFACTOR)

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        self.lbl_input = QtWidgets.QLabel(os.path.basename(self.input_file))
        self.grid.addWidget(self.lbl_input, 0, 0, 1, 1,)

        self.lbl_output = QtWidgets.QLabel(os.path.basename(self.output_file))
        self.grid.addWidget(self.lbl_output, 0, 1, 1, 1)

        self.lbl_input_pic = QtWidgets.QLabel("Loading...")
        self.grid.addWidget(self.lbl_input_pic, 1, 0, 1, 1)

        self.lbl_output_pic = QtWidgets.QLabel("Loading...")
        self.grid.addWidget(self.lbl_output_pic, 1, 1, 1, 1)

        self.btn_back = QtWidgets.QPushButton("Close visualisation")
        self.grid.addWidget(self.btn_back, 2, 0, 1, 2)

        self.btn_back.clicked.connect(self.func_back)

        input_pngname = os.path.join(self.parent.workingDirectory, os.path.basename(self.input_file).rsplit(".", 1)[0] + ".png")
        drawP.drawXML(self.input_file, input_pngname)

        self.pixm_in = QtGui.QPixmap(input_pngname)
        self.lbl_input_pic.setPixmap(self.pixm_in)
        self.lbl_input_pic.setScaledContents(True)
        self.lbl_input_pic.setFixedSize(QtCore.QSize(400*SIZEFACTOR, 400*SIZEFACTOR))

        if os.path.isfile(self.output_file):
            output_pngname = os.path.join(self.parent.workingDirectory, os.path.basename(self.output_file).rsplit(".", 1)[0] + ".png")
            drawP.drawXML(self.output_file, output_pngname)
            self.pixm_out = QtGui.QPixmap(output_pngname)
            self.lbl_output_pic.setPixmap(self.pixm_out)
            self.lbl_output_pic.setScaledContents(True)
            self.lbl_output_pic.setFixedSize(QtCore.QSize(400*SIZEFACTOR, 400*SIZEFACTOR))
        else:
            self.lbl_output_pic.setText("please transform file first")

        self.scale = 1
        self.lbl_input_pic.installEventFilter(self)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched is self.lbl_input_pic or watched is self.lbl_output_pic and event.type() == QtCore.QEvent.Wheel:
            if 'angleDelta' in dir(event):
                if self.lbl_input_pic.underMouse():
                    pos = self.lbl_input.mapFromGlobal(QtGui.QCursor.pos())
                elif self.lbl_output_pic.underMouse():
                    pos = self.lbl_output.mapFromGlobal(QtGui.QCursor.pos())
                x, y = pos.x(), pos.y()
                if event.angleDelta().y() > 0:
                    self.scale *= 0.9
                    img_in = self.pixm_in.toImage()
                    img_out = self.pixm_out.toImage()
                    scaled = img_in.height() * self.scale
                    x *= img_in.width() /self.lbl_input_pic.width()
                    y *= img_in.height() /self.lbl_input_pic.height()
                    img_in_copy = img_in.copy(max(0, min(x - (scaled / 2), 1000 - scaled)),max(0, min(y - (scaled / 2), 1000 - scaled)), scaled, scaled)
                    img_out_copy = img_out.copy(max(0, min(x - (scaled / 2), 1000 - scaled)),max(0, min(y - (scaled / 2), 1000 - scaled)), scaled, scaled)
                    self.lbl_input_pic.setPixmap(QtGui.QPixmap(img_in_copy))
                    self.lbl_output_pic.setPixmap(QtGui.QPixmap(img_out_copy))
                elif event.angleDelta().y() < 0:
                    self.scale /= 0.9
                    if self.scale >= 1:
                        self.scale = 1
                        self.lbl_input_pic.setPixmap(self.pixm_in)
                        self.lbl_output_pic.setPixmap(self.pixm_out)
                    img_out = self.pixm_out.toImage()
                    img_in = self.pixm_in.toImage()
                    scaled = img_in.height() * self.scale
                    x *= img_in.width() /self.lbl_input_pic.width()
                    y *= img_in.height() /self.lbl_input_pic.height()
                    img_in_copy = img_in.copy(max(0, min(x - (scaled / 2), 1000 - scaled)),max(0, min(y - (scaled / 2), 1000 - scaled)), scaled, scaled)
                    img_out_copy = img_out.copy(max(0, min(x - (scaled / 2), 1000 - scaled)),max(0, min(y - (scaled / 2), 1000 - scaled)), scaled, scaled)
                    self.lbl_input_pic.setPixmap(QtGui.QPixmap(img_in_copy))
                    self.lbl_output_pic.setPixmap(QtGui.QPixmap(img_out_copy))
        return super().eventFilter(watched, event)

    def func_back(self):
        self.parent.show()
        self.hide()
    

class VisualisationThread(QtCore.QThread):
    finished = QtCore.Signal(str)
    def __init__(self, filename: str) -> None:
        super(VisualisationThread, self).__init__()
        self.filename = filename

    def run(self) -> None:
        print(f"rendering {self.filename}")
        pngname = self.filename.rsplit(".", 1)[0] + ".png"
        drawP.drawXML(self.filename, pngname)
        # print(f"dummy drawing {self.filename}")
        # # time.sleep(3)
        # dummy.bing(self.filename, pngname)
        print("done drawing")
        self.finished.emit(pngname)

    
class ValidationWindow(QtWidgets.QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super(ValidationWindow, self).__init__()
        self.parent = parent
        self.input_file = self.parent.filename_input
        self.output_file = self.parent.workingDirectory + "/Transformation_Result.gml"
        self.initUI()

    def initUI(self) -> None:
        gf.windowSetup(self, POSX +100, POSY +100, WIDTH, HEIGHT, "CityGTV - CityGML Validation", SIZEFACTOR)


        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.tbl_vali = QtWidgets.QTableWidget()
        self.tbl_vali.setColumnCount(4)
        self.tbl_vali.setHorizontalHeaderLabels(["Filename", "NO. of Buildings in Total:", "NO. of Buildings Invalid:", "NO. of Invalid Polygons:"])
        self.tbl_vali.verticalHeader().hide()
        for i in range(self.tbl_vali.columnCount()):
            self.tbl_vali.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        self.vbox.addWidget(self.tbl_vali)

        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox.addLayout(self.hbox)

        self.btn_save_in = QtWidgets.QPushButton("Save input file validation report")
        self.btn_save_in.setEnabled(False)
        self.hbox.addWidget(self.btn_save_in)

        self.btn_save_out = QtWidgets.QPushButton("Save output file validation report")
        self.btn_save_out.setEnabled(False)
        self.hbox.addWidget(self.btn_save_out)

        self.btn_back = QtWidgets.QPushButton("Close validation results")
        self.vbox.addWidget(self.btn_back)

        self.btn_back.clicked.connect(self.func_close)
        self.btn_save_in.clicked.connect(functools.partial(self.saveReport, True))
        self.btn_save_out.clicked.connect(functools.partial(self.saveReport, False))

        self.report_in = None
        self.report_out = None
        self.thread_vali = ValidationThread()

        self.validate_file(self.input_file, True)

            


    def func_close(self) -> None:
        self.parent.show()
        self.hide()


    def validate_file(self, filename: str, is_input: bool):
        """validates citygml file"""
        buildingList = valP.v_readCityGML(filename, self.parent._nameSpace)
        print("Number buildings = ",len(buildingList))

        self.thread_vali = ValidationThread()
        self.thread_vali.filename = filename
        self.thread_vali.buildingList = buildingList
        self.thread_vali.isInput = is_input
        self.thread_vali.finished.connect(self.validationCompleted)
        self.thread_vali.start()


    def validationCompleted(self, is_input:bool):
        """displays validation results"""

        report_str = ""
        num_invalid_geometry = 0
        num_invalid_building = 0

        buildingResult = self.thread_vali.buildingResult

        for i in range(len(buildingResult)):
            invalidOne = buildingResult[i]
            if invalidOne.cmt == "Valid":
                continue
            else:
                num_invalid_building += 1
                for roof in invalidOne.roof:
                    if roof.cmt != "Valid":
                        num_invalid_geometry += 1
                        newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
                        ";\n\n Roof Issue = "+str(roof.name)+"\n\n"+str(roof.cmt)+\
                        "------------------------------------------------------------------------\n\n"
                        #print("Building No ",i,">>",newInvalidStr)
                        report_str += newInvalidStr
                for foot in invalidOne.foot:
                    if foot.cmt != "Valid":
                        num_invalid_geometry += 1
                        newInvalidStr = str(num_invalid_geometry)+". In This Building = "\
                        +str(invalidOne.name)+\
                        ";\n\n Foot Issue = "+str(foot.name)+"\n\n"+str(foot.cmt)+\
                        "------------------------------------------------------------------------\n\n"   
                        #print("Building No ",i,">>",newInvalidStr)
                        report_str += newInvalidStr
                for wall in invalidOne.wall:
                    if wall.cmt != "Valid":
                        num_invalid_geometry += 1
                        newInvalidStr = str(num_invalid_geometry)+". In Building = "+str(invalidOne.name)+\
                        ";\n\n Wall Issue = "+str(wall.name)+"\n\n"+str(wall.cmt)+\
                        "------------------------------------------------------------------------\n\n"   
                        #print("Building No ",i,">>",newInvalidStr)
                        report_str += newInvalidStr


        
        row_count = self.tbl_vali.rowCount()
        self.tbl_vali.insertRow(row_count)
        for i, entry in enumerate([os.path.basename(self.thread_vali.filename), len(buildingResult), num_invalid_building, num_invalid_geometry]):
            item = QtWidgets.QTableWidgetItem(str(entry))
            self.tbl_vali.setItem(row_count, i, item)

        print("number of invalid LinearRings = ",num_invalid_geometry)
        print("cpu_count = ",mp.cpu_count())
        print("number of invalid Buildings = ",num_invalid_building,"/",len(buildingResult))
        
        if is_input:
            self.report_in = report_str
            self.btn_save_in.setEnabled(True)
            if os.path.isfile(self.output_file):
                self.validate_file(self.output_file, False)
        else:
            self.report_out = report_str
            self.btn_save_out.setEnabled(True)



    def saveReport(self, is_input:bool) -> None:
        if is_input:
            self.fileNameReport_input = self.parent.workingDirectory+"/Validation_report_for_inputGML.txt"
            with open(self.fileNameReport_input,'w') as f_handle:
                f_handle.write(self.report_in)
        else:
            self.fileNameReport_output = self.parent.workingDirectory+"/Validation_report_for_outputGML.txt"
            with open(self.fileNameReport_output,'w') as f_handle:
                f_handle.write(self.report_out)

        gf.messageBox(self, "Info", "Validation Report Saved")




class ValidationThread(QtCore.QThread):
    finished = QtCore.Signal(bool)
    def __init__(self, parent=None):
        super(ValidationThread, self).__init__(parent)
        self.filename = ""
        self.buildingList = []
        self.manager = mp.Manager()
        self.buildingResult = self.manager.list()
        self.isInput = True

    def run(self):
        #self.do_work()

        pool = mp.Pool()
        pool.starmap(valP.validation,\
            [(self.buildingList,self.buildingResult,loc) for loc in range(len(self.buildingList))])

        pool.close()
        pool.join()
        
        # Update buildingList with the buildingResult, which contains the transformation results.
        print("number of results",len(self.buildingResult))
        print("cpu_count = ",mp.cpu_count())
          
        self.finished.emit(self.isInput)





class TransformationWindow(QtWidgets.QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super(TransformationWindow, self).__init__()
        self.parent = parent
        self.input_file = self.parent.filename_input
        self.output_file = self.parent.workingDirectory + "/Transformation_Result.gml"
        self.initUI()


    def initUI(self):
        gf.windowSetup(self, POSX +100, POSY +100, WIDTH, HEIGHT + (300*SIZEFACTOR), "CityGTV - CRS Transformation", SIZEFACTOR)

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        
        self.groupB_crs = QtWidgets.QGroupBox()
        self.vbox.addWidget(self.groupB_crs)

        self.crs_grid = QtWidgets.QGridLayout()
        self.groupB_crs.setLayout(self.crs_grid)

        self.lbl_input_crs = QtWidgets.QLabel("Input CRS")
        self.crs_grid.addWidget(self.lbl_input_crs, 0, 0, 1, 1)

        self.lbl_output_crs = QtWidgets.QLabel("Output CRS")
        self.crs_grid.addWidget(self.lbl_output_crs, 0, 1, 1, 1)

        epsgList = ['epsg:5555 DE','epsg:5834 DE','epsg:23032 EU','epsg:25832 EU','epsg:27700 UK']

        self.combB_input_crs = QtWidgets.QComboBox()
        self.combB_input_crs.addItems(epsgList)
        self.crs_grid.addWidget(self.combB_input_crs, 1, 0, 1, 1)

        self.combB_output_crs = QtWidgets.QComboBox()
        self.combB_output_crs.addItems(epsgList)
        self.crs_grid.addWidget(self.combB_output_crs, 1, 1, 1, 1)


        self.groupB_coor = QtWidgets.QGroupBox()
        self.vbox.addWidget(self.groupB_coor)

        self.coor_grid = QtWidgets.QGridLayout()
        self.groupB_coor.setLayout(self.coor_grid)

        self.lbl_coor_title = QtWidgets.QLabel("Please edit your destination here: [Lon, Lat] from EPSG 4326 (in degree)")
        self.coor_grid.addWidget(self.lbl_coor_title, 0, 0, 1, 30)

        self.lbl_lat = QtWidgets.QLabel("Lat=")
        self.coor_grid.addWidget(self.lbl_lat, 1, 0, 1, 6)

        self.txtB_lat = QtWidgets.QLineEdit("")
        self.txtB_lat.setPlaceholderText("50.775428")
        self.coor_grid.addWidget(self.txtB_lat, 1, 6, 1, 6)

        self.lbl_lon = QtWidgets.QLabel("Lon=")
        self.coor_grid.addWidget(self.lbl_lon, 1, 12, 1, 6)

        self.txtB_lon = QtWidgets.QLineEdit("")
        self.txtB_lon.setPlaceholderText("6.083808")
        self.coor_grid.addWidget(self.txtB_lon, 1, 18, 1, 6)

        self.btn_transform_desitnation = QtWidgets.QPushButton("Transform to [X,Y,Z] for Output CRS")
        self.coor_grid.addWidget(self.btn_transform_desitnation, 1, 24, 1, 6)

        self.coor_grid.setRowMinimumHeight(2, 10)

        self.lbl_destination = QtWidgets.QLabel("Destination in [X,Y,Z]")
        self.coor_grid.addWidget(self.lbl_destination, 3, 0, 1, 30)

        self.lbl_output_bounds = QtWidgets.QLabel("Coordinates shall fall within th projected bounds of the output CRS")
        self.coor_grid.addWidget(self.lbl_output_bounds, 4, 0, 1, 30)

        self.lbl_x = QtWidgets.QLabel("X=")
        self.coor_grid.addWidget(self.lbl_x, 5, 0, 1, 5)

        self.txtB_x = QtWidgets.QLineEdit("")
        self.txtB_x.setEnabled(False)
        self.coor_grid.addWidget(self.txtB_x, 5, 5, 1, 5)

        self.lbl_y = QtWidgets.QLabel("Y=")
        self.coor_grid.addWidget(self.lbl_y, 5,  10, 1, 5)

        self.txtB_y = QtWidgets.QLineEdit("")
        self.txtB_y.setEnabled(False)
        self.coor_grid.addWidget(self.txtB_y, 5, 15, 1, 5)

        # self.lbl_z = QtWidgets.QLabel("Z=")
        # self.coor_grid.addWidget(self.lbl_z, 5, 20, 1, 5)

        # self.txtB_z = QtWidgets.QLineEdit("")
        # self.txtB_z.setEnabled(True)
        # self.coor_grid.addWidget(self.txtB_z, 5, 25, 1, 5)


        self.groupB_rotation = QtWidgets.QGroupBox("Rotation")
        self.groupB_rotation.setCheckable(True)
        self.groupB_rotation.setChecked(False)
        self.vbox.addWidget(self.groupB_rotation)

        self.rot_grid = QtWidgets.QGridLayout()
        self.groupB_rotation.setLayout(self.rot_grid)

        self.lbl_rotation_description = QtWidgets.QLabel("Use Center of input CityGML file as pivot point")
        self.rot_grid.addWidget(self.lbl_rotation_description, 0, 0, 1, 4)

        self.lbl_rotation_input = QtWidgets.QLabel("Please enter roation in degree [-360,360]:")
        self.rot_grid.addWidget(self.lbl_rotation_input, 1, 0, 1, 3)

        self.txtB_rotation = QtWidgets.QLineEdit("0")
        self.txtB_rotation.setToolTip("A positive angle will rotate buildings in a counterclockwise direction\nA negative value will rotate buildings in a clockwise direction")
        self.rot_grid.addWidget(self.txtB_rotation, 1, 3, 1, 3)


        self.groupB_elevation = QtWidgets.QGroupBox("Enable elevation transfromation")
        self.groupB_elevation.setCheckable(True)
        self.groupB_elevation.setChecked(False)
        self.vbox.addWidget(self.groupB_elevation)

        self.ele_grid = QtWidgets.QGridLayout()
        self.groupB_elevation.setLayout(self.ele_grid)

        self.lbl_elevation = QtWidgets.QLabel("Please enter elevation value")
        self.ele_grid.addWidget(self.lbl_elevation, 1, 0, 1, 3)

        self.txtB_elevation = QtWidgets.QLineEdit("0")
        self.ele_grid.addWidget(self.txtB_elevation, 1, 3, 1, 3)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.vbox.addWidget(self.progressBar)


        self.btn_transformation_start = QtWidgets.QPushButton("Start Transformation")
        self.btn_transformation_start.clicked.connect(self.transformXML)
        self.vbox.addWidget(self.btn_transformation_start)

        self.btn_back = QtWidgets.QPushButton("Back")
        self.vbox.addWidget(self.btn_back)


        self.btn_transform_desitnation.clicked.connect(self.transformLonLat)
        self.btn_back.clicked.connect(self.close_transformation)


        self.groupB_elevation.setEnabled(True)
        self.groupB_rotation.setEnabled(True)

        self.buildingSelectionList = []


    def transformLonLat(self):
        """To-Do: description"""
        try:
            lon = float(self.txtB_lon.text())
            lat = float(self.txtB_lat.text())
        except:
            gf.messageBox(self, "Error", "Failed to convert inputs to floats")
            return 1

        wgs = pyproj.CRS("EPSG:4326")
        OutProj = pyproj.CRS(self.combB_output_crs.currentText().split(" ")[0])
        
        try:
            x,y = pyproj.transform(wgs,OutProj,lat,lon)

            self.txtB_x.setText(str(x))
            self.txtB_y.setText(str(y))
            # self.txtB_z.setText("0")

        except:
            gf.messageBox(self, "Error", "Error within CRS transformation")
            return 1

        # Initialize the selectionReference, 
        # by default all buildings will be selected for rotation/elevation transformation
        for building in self.parent.buildingList:
            self.buildingSelectionList.append(str(building.name).split("'")[-2])
        # enable check boxes
        self.groupB_elevation.setEnabled(True)
        self.groupB_rotation.setEnabled(True)


    def transformXML(self):
        start_time = time.time()

        # target location: values are in target CRS
        tp_x = 0
        tp_y = 0
        tp_z = 0
        #Angle & Elevation
        angle = 0
        elevationChange = 0
        try:
            tp_x = float(self.txtB_x.text())
            tp_y = float(self.txtB_y.text())
            tp_z = 0
            angle = float(self.txtB_rotation.text())
            elevationChange = float(self.txtB_elevation.text())
        except:
            gf.messageBox(self, "Warning", "Please Transform the LatLon to XYZ-coordinates.")
            return 1

        targetLoc = [tp_x,tp_y,tp_z]

        # start to transform
        fileName = self.input_file
        fileName_exported = self.output_file
        if fileName=="" or fileName_exported=="":
            print("Files are not ready.")
            return 1

        # in&out projected CRS, format: "epsg:xxxx"
        inputCRS_str = self.combB_input_crs.currentText()
        outputCRS_str = self.combB_output_crs.currentText()
        inputCRS_str = inputCRS_str.split(" ")[0]
        outputCRS_str = outputCRS_str.split(" ")[0]
 
        inProj = pyproj.Proj(inputCRS_str)
        outProj = pyproj.Proj(outputCRS_str)  

        # check if the target point is in the range of the output_CRS
        # get the CRS for output
        print("outputCRS = ",outputCRS_str.split(':')[-1])
        outputCRS = pyproj.CRS.from_epsg(int(outputCRS_str.split(':')[-1]))
        print("outputCRS.area_of_use (W,S,E,N)",outputCRS.area_of_use.west,', ',\
            outputCRS.area_of_use.south,', ',outputCRS.area_of_use.east,', ',\
            outputCRS.area_of_use.north)

        # the boundary of output CRS is presented by two corners, (west,south) and (east,north)
        # project these two points from degree to meter: 
        # "outProj(west,south)" gives the bottom-left corner in the unit of meter.

        x_west,y_south = outProj(outputCRS.area_of_use.west,outputCRS.area_of_use.south)
        x_east,y_north = outProj(outputCRS.area_of_use.east,outputCRS.area_of_use.north)

        # now check if our target point is within the boundary of outputCRS
        if (tp_x >= x_west and tp_x <= x_east) and (tp_y >= y_south and tp_y <= y_north):
            print("Target point falls within the boundary of outProj.")
        else:
            gf.messageBox(self, "Error", \
                "Target point [x,y,z] out of the projected bounds of the output CRS.\nPlease re-enter tartget point or choose other output CRS.")
            return 1

        print("========================================")


        # save the xml data into buildingList. To call the building inside it, 
        # use buildingList[x].name or buildingList[x].roof (.foor or .wall) 


        # parse the xml file
        tree = ET.parse(fileName)

        # find the REF point and OFFSET vector.
        pt_REF = xmlPP.getREF(tree.getroot(),self.parent._nameSpace,inProj,outProj)
        OFFSET = np.subtract(np.array(targetLoc),np.array(pt_REF))
        OFFSET[2] = 0

        # establish QThread
        self.workerThread = WorkerThread()
        self.workerThread.finished.connect(self.transformationCompleted)

        self.workerThread.buildingList = self.parent.buildingList
        self.workerThread.OFFSET = OFFSET
        self.workerThread.inputCRS = inputCRS_str
        self.workerThread.outputCRS = outputCRS_str
        self.workerThread.angle = angle
        self.workerThread.elevationChange = elevationChange
        self.workerThread.fileName_input = fileName
        self.workerThread.fileName_exported = fileName_exported
        self.workerThread.selectionReference = self.buildingSelectionList
        self.workerThread._nameSpace = self.parent._nameSpace

        # make progressBar alive
        self.progressBar.setRange(0,len(self.parent.buildingList))
        self.progressBar.setValue(0)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.updateProgressBar)
        timer.start(100)

        #disable "start" button once the thread begins
        self.btn_transformation_start.setEnabled(False)
        self.workerThread.start()

        return 0

    def transformationCompleted(self,executionTime):
        self.btn_transformation_start.setEnabled(True)

        time_str = str(executionTime)[0:6]
        gf.messageBox(self, "Transformation completed", "Transformation Completed in "+time_str+" Seconds.")

        #enable the output button in VisualisationWindow.
        self.parent.isTransformed=True

    def updateProgressBar(self):
        self.progressBar.setValue(len(self.workerThread.buildingResult))

    def close_transformation(self):
        # back to MainWindow and close the sub-window.
        if self.parent.isTransformed == True:
            self.parent.btn_validation.setEnabled(True)
        self.parent.show()
        self.close()
        return 0


# using Thread to avoid freezing the UI while processing some heavy work.
# Thread for transformation via multiprocessing
class WorkerThread(QtCore.QThread):
    finished = QtCore.Signal(float)
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)

        self.buildingList = []

        self.manager = mp.Manager()
        self.buildingResult = self.manager.list()

        self.OFFSET = np.array([0,0,0])
        self.inputCRS = ""
        self.outputCRS = ""
        self.angle = 0
        self.elevationChange = 0
        self.fileName_input = ""
        self.fileName_exported = ""
        self.selectionReference = []
        self._nameSpace = {"key":"value"}

    def run(self):
        #self.do_work()
        start_time = time.time()

        inProj = pyproj.Proj(self.inputCRS)
        outProj = pyproj.Proj(self.outputCRS)

        pool = mp.Pool()
        pool.starmap(xmlPP.crsTransformPool,\
            [(self.buildingList,self.buildingResult,loc,self.OFFSET,inProj,outProj,\
                self.angle,self.elevationChange,self.selectionReference) \
           for loc in range(len(self.buildingList))])

        pool.close()
        pool.join()
        
        # Update buildingList with the buildingResult, which contains the transformation results.
        print("number of results",len(self.buildingResult))
        print("cpu_count = ",mp.cpu_count())
        print("Transformation completed successfully.")
        
        # export the List to an XML
        xmlPP.treeWriter(self.fileName_exported,ET.parse(self.fileName_input),\
            self.buildingResult,self._nameSpace)
        
        self.finished.emit(float(time.time()-start_time))

        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.aboutToQuit.connect(app.deleteLater)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())