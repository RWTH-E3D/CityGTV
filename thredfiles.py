import numpy as np
import os
import sys
import PySide2
from PySide2 import QtWidgets, QtGui,QtCore
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue, Pool
from pyproj import Proj, transform, CRS
# import transform_func as tf
import xml.etree.ElementTree as ET
import time
# import validation_Process as vp
# import visualize_GML as vg
import xmlParser_Process as xp
# --------------------------------------------------
# using Thread to avoid freezing the UI while processing some heavy work.
# Thread for transformation via multiprocessing
class WorkerThread(QtCore.QThread):
    # finished = QtCore.Signal(float)
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)

        self.buildingList = []

        self.manager = Manager()
        self.buildingResult = self.manager.list()

        self.OFFSET = np.array([0 ,0 ,0])
        self.inputCRS = ""
        self.outputCRS = ""
        self.angle = 0
        self.elevationChange = 0
        self.fileName_input = ""
        self.fileName_exported = ""
        self.selectionReference = []
        self._nameSpace = {"key" :"value"}

    def run(self):
        # self.do_work()
        start_time = time.time()

        inProj = Proj(self.inputCRS)
        outProj = Proj(self.outputCRS)

        pool = Pool()
        pool.starmap(tf.crsTransformPool, \
                     [(self.buildingList ,self.buildingResult ,loc ,self.OFFSET ,inProj ,outProj, \
                       self.angle ,self.elevationChange ,self.selectionReference) \
                      for loc in range(len(self.buildingList))])

        pool.close()
        pool.join()

        # Update buildingList with the buildingResult, which contains the transformation results.
        print("number of results" ,len(self.buildingResult))
        print("cpu_count = " ,mp.cpu_count())
        print("Transformation completed successfully.")

        # export the List to an XML
        tf.treeWriter(self.fileName_exported ,ET.parse(self.fileName_input), \
                   self.buildingResult ,self._nameSpace)

        # self.finished.emit(float(time.time( ) -start_time))


# Thread for drawing.
class DrawingThread(QtCore.QThread):
    # finished = QtCore.Signal(bool)
    def __init__(self, parent=None):
        super(DrawingThread, self).__init__(parent)
        self.fileName_xml = ""
        self.fileName_png = ""
        self.myDPI = 600
        self.isInput = True

    def run(self):
        print("Export .png file to the working directory:\n " +self.fileName_png)
        vg.drawXML(self.fileName_xml, self.fileName_png, self.myDPI)
        # self.finished.emit(self.isInput)

class ValidationThread(QtCore.QThread):
    # finished = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(ValidationThread, self).__init__(parent)
        self.buildingList = []
        self.manager = Manager()
        self.buildingResult = self.manager.list()
        self.isInput = True

    def run(self):
        # self.do_work()
        start_time = time.time()

        pool = Pool()
        pool.starmap(vp.validation, \
                     [(self.buildingList ,self.buildingResult ,loc) for loc in range(len(self.buildingList))])

        pool.close()
        pool.join()

        # Update buildingList with the buildingResult, which contains the transformation results.
        print("number of results" ,len(self.buildingResult))
        print("cpu_count = " ,mp.cpu_count())

        # self.finished.emit([time.time() - start_time, self.isInput])
