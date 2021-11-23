from PySide2 import QtWidgets, QtCore
# import pyproj
# import math
from pyproj import Proj, transform, CRS
# import xmlParser_Process as xp
import CityGTV_gui_func as gf
# import thredfiles as td
#
# import time
# import glob
# import os
# import lxml.etree as ET
# import matplotlib.path as mpl
# import numpy as np
# from math import sin,cos
# import csv
# # import validation_Process as vp


import CityGTV_gui_func as gtvgf
import CityGTVmain as gtvmain


def transformLonLat(self):
    if self.QL_x.text() != '' and self.QL_y.text() != '':
        try:
            lon = float(self.QL_x.text())
            lat = float(self.QL_y.text())
        except:
            gf.messageBox(self, 'Important',"Please enter valid number!")
            return 1

        InProj = CRS(self.combobox_input.currentText())
        # wgs = CRS("EPSG:4326")
        OutProj = CRS(self.combobox_output.currentText())

        try:
            x, y = transform(InProj, OutProj, lat, lon)

            self.x_user.setText(str(x))
            self.y_user.setText(str(y))

        except:
            gf.messageBox(self, 'Important',"CRS error")
            return 1

    else:
        gf.messageBox(self, 'Important', "Please enter valid coordinates")

def reset_coordinate_selection(self):
    self.QL_x.clear()
    self.QL_x.setPlaceholderText('Longitude')
    self.x_user.clear()
    self.x_user.setPlaceholderText('X coordinate entered')
    self.QL_y.clear()
    self.QL_y.setPlaceholderText('Latitude')
    self.y_user.clear()
    self.y_user.setPlaceholderText('X coordinate entered')
    self.combobox_input.setCurrentIndex(0)
    self.combobox_output.setCurrentIndex(0)

def delpoint(self):
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', "Do you want to delete the added coordinates?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        reset_coordinate_selection(self)
    else:
        pass

def transformmodels(self):
    # target location: values are in target CRS. and this is a location in London:
    tp_x = 0
    tp_y = 0
    tp_z = 0
    #Angle & Elevation
    angle = 0
    elevationChange = 0
    try:
        tp_x = float(self.x_user.text())
        tp_y = float(self.y_user.text())
        tp_z = float(0)
        angle = float(self.line_rotation.text())
        elevationChange = float(self.line_elevation.text())
    except:
        self.msgBoxCreator("Please Transform the LatLon to XYZ-coordinates.")
        return 1

    targetLoc = [tp_x,tp_y,tp_z, angle, elevationChange]
    print(targetLoc)

def close_application(self):
    """quit dialog, to confirm exiting"""
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', 'Do you want to quit?',
                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
    else:
        pass

def back_btn(self):
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', "Do you want to go back to the CityGTV main?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        gtvgf.next_window(self, gtvmain.mainWindow())
    else:
        pass


# def getCenter(building):
#     center = [0, 0]
#     min_x = building.foot[0][0]
#     max_x = building.foot[0][0]
#     min_y = building.foot[0][1]
#     max_y = building.foot[0][1]
#
#     for foot in building.foot:
#         for i in range(int(len(foot) / 3)):
#             if foot[3 * i] < min_x:
#                 min_x = foot[3 * i]
#             elif foot[3 * i] > max_x:
#                 max_x = foot[3 * i]
#             if foot[3 * i + 1] < min_y:
#                 min_y = foot[3 * i + 1]
#             elif foot[3 * i + 1] > max_y:
#                 max_y = foot[3 * i + 1]
#     center[0] = float((min_x + max_x) / 2)
#     center[1] = float((min_y + max_y) / 2)
#     return center
# # export the xml file
# def treeWriter(fileName_exported,tree,buildingList,_nameSpace):
#     root = tree.getroot()
#     for bldg in root.findall(".//bldg:Building",_nameSpace):
#         for building in buildingList:
#             if str(bldg.attrib) == str(building.name):
#                 # roof
#                 roof_mark = 0
#                 for pts in bldg.findall(".//bldg:RoofSurface//gml:posList",_nameSpace):
#                     transformedList = ['{:.8f}'.format(x) for x in building.roof[roof_mark]]
#                     seperator = ' '
#                     pts.text = seperator.join(transformedList)
#                     roof_mark += 1
#                 # foot
#                 foot_mark = 0
#                 for pts in bldg.findall(".//bldg:GroundSurface//gml:posList",_nameSpace):
#                     transformedList = ['{:.8f}'.format(x) for x in building.foot[foot_mark]]
#                     seperator = ' '
#                     pts.text = seperator.join(transformedList)
#                     foot_mark += 1
#                 # wall
#                 wall_mark = 0
#                 for pts in bldg.findall(".//bldg:WallSurface//gml:posList",_nameSpace):
#                     transformedList = ['{:.8f}'.format(x) for x in building.wall[wall_mark]]
#                     seperator = ' '
#                     pts.text = seperator.join(transformedList)
#                     wall_mark += 1
#         # end loop of searching for the building with same name, and go for the next building.
#     # end loop of all buildings
#
#     # ElementTree has to register all the nameSpaces(xmlns) manually. Otherwise, the export'll be wrong.
#     for key in _nameSpace.keys():
#         ET.register_namespace(str(key),str(_nameSpace[key]))
#
#     # change the output file name here:
#     tree.write(fileName_exported,xml_declaration=True,encoding='utf-8', method="xml")
#     return 0
#
# def crsTransformPool(buildingList, buildingResult, loc, OFFSET, inProj, outProj, angle, elevation, selectionReference):
#     print("process starts = ", loc)
#     # single_start_time = time.time()
#     proxy = buildingList[loc]
#     angle = angle / 180 * (np.pi)
#
#     # selection Reference, to determine whether it is necessary to do the rotation and elevation transformation.
#     buildingName = str(proxy.name).split("'")[-2]
#
#     # pivot in the original CRS
#     pivot = getCenter(proxy)
#     resX, resY = transform(inProj, outProj, pivot[0], pivot[1])
#     pivot = [resX + OFFSET[0], resY + OFFSET[1]]
#
#     # roof
#     for rj in range(len(proxy.roof)):
#         # select the j_th roof in ".roof"
#         posList = proxy.roof[rj]
#         for k in range(int(len(posList) / 3)):
#             res_x, res_y = transform(inProj, outProj, posList[3 * k], posList[3 * k + 1])
#             res_x = res_x + OFFSET[0]
#             res_y = res_y + OFFSET[1]
#             if buildingName in selectionReference:
#                 dx = (res_x - pivot[0]) * cos(angle) - (res_y - pivot[1]) * sin(angle)
#                 dy = (res_x - pivot[0]) * sin(angle) + (res_y - pivot[1]) * cos(angle)
#                 proxy.roof[rj][3 * k] = dx + pivot[0]
#                 proxy.roof[rj][3 * k + 1] = dy + pivot[1]
#                 proxy.roof[rj][3 * k + 2] += elevation
#             else:
#                 proxy.roof[rj][3 * k] = res_x
#                 proxy.roof[rj][3 * k + 1] = res_y
#                 # foot
#     for fj in range(len(proxy.foot)):
#         posList = proxy.foot[fj]
#         for k in range(int(len(posList) / 3)):
#             res_x, res_y = transform(inProj, outProj, posList[3 * k], posList[3 * k + 1])
#             res_x = res_x + OFFSET[0]
#             res_y = res_y + OFFSET[1]
#             if buildingName in selectionReference:
#                 dx = (res_x - pivot[0]) * cos(angle) - (res_y - pivot[1]) * sin(angle)
#                 dy = (res_x - pivot[0]) * sin(angle) + (res_y - pivot[1]) * cos(angle)
#                 proxy.foot[fj][3 * k] = dx + pivot[0]
#                 proxy.foot[fj][3 * k + 1] = dy + pivot[1]
#                 proxy.foot[fj][3 * k + 2] += elevation
#             else:
#                 proxy.foot[fj][3 * k] = res_x
#                 proxy.foot[fj][3 * k + 1] = res_y
#     # wall
#     for wj in range(len(proxy.wall)):
#         posList = proxy.wall[wj]
#         for k in range(int(len(posList) / 3)):
#             res_x, res_y = transform(inProj, outProj, posList[3 * k], posList[3 * k + 1])
#             res_x = res_x + OFFSET[0]
#             res_y = res_y + OFFSET[1]
#             if buildingName in selectionReference:
#                 dx = (res_x - pivot[0]) * cos(angle) - (res_y - pivot[1]) * sin(angle)
#                 dy = (res_x - pivot[0]) * sin(angle) + (res_y - pivot[1]) * cos(angle)
#                 proxy.wall[wj][3 * k] = dx + pivot[0]
#                 proxy.wall[wj][3 * k + 1] = dy + pivot[1]
#                 proxy.wall[wj][3 * k + 2] += elevation
#             else:
#                 proxy.wall[wj][3 * k] = res_x
#                 proxy.wall[wj][3 * k + 1] = res_y
#     # save the transformed results
#     buildingResult.append(proxy)
#     # print("---In a single loop: %s seconds ---" % (time.time() - single_start_time))
#     print("process ends = ", loc)
#     return 0

# def transformXML(self):
#     start_time = time.time()
#
#     # target location: values are in target CRS. and this is a location in London:
#     tp_x = 0
#     tp_y = 0
#     tp_z = 0
#     # Angle & Elevation
#     angle = 0
#     elevationChange = 0
#     try:
#         tp_x = float(self.x_user.text())
#         tp_y = float(self.y_user.text())
#         tp_z = float(0)
#         angle = float(self.line_rotation.text())
#         elevationChange = float(self.line_elevation.text())
#     except:
#         self.msgBoxCreator("Please Transform the LatLon to XYZ-coordinates.")
#         return 1
#
#     targetLoc = [tp_x, tp_y, tp_z, angle, elevationChange]
#     print(targetLoc)
#
#     # start to transform
#     headin, tailin = os.path.split(self.textbox_gml.text())
#     fileName = tailin
#     pathout = os.path.split(self.textbox_gml_folder.text())
#     fileName_exported = pathout+'/CityLDTout.gml'
#     if fileName == "" or fileName_exported == "":
#         print("Files are not ready.")
#         return 1
#
#     # in&out projected CRS, format: "epsg:xxxx"
#     inputCRS_str = self.cmb_input_crs.currentText()
#     outputCRS_str = self.cmb_output_crs.currentText()
#     inputCRS_str = inputCRS_str.split(" ")[0]
#     outputCRS_str = outputCRS_str.split(" ")[0]
#
#     inProj = Proj(inputCRS_str)
#     outProj = Proj(outputCRS_str)
#
#     # check if the target point is in the range of the output_CRS
#     # get the CRS for output
#     print("outputCRS = ", outputCRS_str.split(':')[-1])
#     outputCRS = CRS.from_epsg(int(outputCRS_str.split(':')[-1]))
#     print("outputCRS.area_of_use (W,S,E,N)", outputCRS.area_of_use.west, ', ', \
#           outputCRS.area_of_use.south, ', ', outputCRS.area_of_use.east, ', ', \
#           outputCRS.area_of_use.north)
#
#     # the boundary of output CRS is presented by two corners, (west,south) and (east,north)
#     # project these two points from degree to meter:
#     # "outProj(west,south)" gives the bottom-left corner in the unit of meter.
#
#     x_west, y_south = outProj(outputCRS.area_of_use.west, outputCRS.area_of_use.south)
#     x_east, y_north = outProj(outputCRS.area_of_use.east, outputCRS.area_of_use.north)
#
#     # now check if our target point is within the boundary of outputCRS
#     if (tp_x >= x_west and tp_x <= x_east) and (tp_y >= y_south and tp_y <= y_north):
#         print("Target point falls within the boundary of outProj.")
#     else:
#         self.msgBoxCreator( \
#             "Target point [x,y,z] out of the projected bounds of the output CRS.\nPlease re-enter tartget point or choose other output CRS.")
#         return 1
#
#     print("========================================")
#
#     # save the xml data into buildingList. To call the building inside it,
#     # use buildingList[x].name or buildingList[x].roof (.foor or .wall)
#     self.buildingList = xp.readCityGML(fileName, self.mainWindow._nameSpace)
#     print("Number buildings = ", len(self.buildingList))
#
#     # parse the xml file
#     tree = ET.parse(fileName)
#
#     # find the REF point and OFFSET vector.
#     pt_REF = xp.getREF(tree.getroot(), gtvmain.mainWindow._nameSpace, inProj, outProj)
#     OFFSET = np.subtract(np.array(targetLoc), np.array(pt_REF))
#     OFFSET[2] = 0
#
#     # establish QThread
#     self.workerThread = td.WorkerThread()
#     self.workerThread.finished.connect(self.transformationCompleted)
#
#     self.workerThread.buildingList = self.buildingList
#     self.workerThread.OFFSET = OFFSET
#     self.workerThread.inputCRS = inputCRS_str
#     self.workerThread.outputCRS = outputCRS_str
#     self.workerThread.angle = angle
#     self.workerThread.elevationChange = elevationChange
#     self.workerThread.fileName_input = fileName
#     self.workerThread.fileName_exported = fileName_exported
#     self.workerThread.selectionReference = self.buildingSelectionList
#     self.workerThread._nameSpace = gtvmain.mainWindow._nameSpace
#
#     # make progressBar alive
#     self.progressBar.setRange(0, len(self.buildingList))
#     self.progressBar.setValue(0)
#
#     timer = QtCore.QTimer(self)
#     timer.timeout.connect(self.updateProgressBar)
#     timer.start(100)
#
#     # disable "start" button once the thread begins
#     self.btn_transform_xml.setEnabled(False)
#     self.workerThread.start()
#
#     # see function transformationCompleted(self) for what will happen once the jone done.
#     # after successful transformation, animate "visualization" and "validation" button
#     gtvmain.mainWindow.animVisualization()
#     gtvmain.mainWindow.animValidation()
#     return 0
