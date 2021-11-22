from PySide2 import QtWidgets, QtCore
import pyproj
import math
from pyproj import Proj, transform, CRS
import xmlParser_Process as xp

import time
import glob
import os
import lxml.etree as ET
import matplotlib.path as mpl
import numpy as np
import csv

import CityGTV_gui_func as gf

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

def transformXML(self):
    # target location: values are in target CRS. and this is a location in London:
    tp_x = 0
    tp_y = 0
    tp_z = 0
    #Angle & Elevation
    angle = 0
    elevationChange = 0
    try:
        tp_x = float(self.edit_targetPoint_x.text())
        tp_y = float(self.edit_targetPoint_y.text())
        tp_z = float(self.edit_targetPoint_z.text())
        angle = float(self.edit_rotation.text())
        elevationChange = float(self.edit_elevation.text())
    except:
        self.msgBoxCreator("Please Transform the LatLon to XYZ-coordinates.")
        return 1

    targetLoc = [tp_x,tp_y,tp_z]