import os
# import teaserplus_gui as tg
from PySide2 import QtWidgets, QtGui, QtCore




def screenSizer(self, posx, posy, width, height, app):
    """func to get size of screen and scale window accordingly"""
    sizefactor = round(app.primaryScreen().size().height()*0.001)              # factor for scaling window, depending on height
    posx *= sizefactor
    posy *= sizefactor
    width *= sizefactor
    height *= sizefactor
    return posx, posy, width, height, sizefactor

def windowSetup(self, posx, posy, width, height, pypath, title, winFac = 1):
    """func for loading icon, setting size and title"""
    try:                                                                            # try to load e3d Icon
        self.setWindowIcon(QtGui.QIcon(os.path.join(pypath, r'pictures\e3dIcon.png')))
    except:
        print('error finding file icon')
    self.setGeometry(posx, posy, width * winFac, height * winFac)                   # setting window size
    self.setFixedSize(width * winFac, height * winFac)                                                # fixing window size
    self.setWindowTitle(title)


def load_banner(self, path, sizefactor, banner_size=150):
    """loading image from path to self.vbox"""
    try:
        self.banner = QtWidgets.QLabel(self)
        self.banner.setPixmap(QtGui.QPixmap(path))
        self.banner.setScaledContents(True)
        self.banner.setMinimumHeight(banner_size*sizefactor)
        self.banner.setMaximumHeight(banner_size*sizefactor)
        self.vbox.addWidget(self.banner)
    except:
        print('error finding banner picture')


def close_application(self):
    """quit dialog, to confirm exiting"""
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', 'Do you want to quit?',
                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
    else:
        pass

def messageBox(self, header, message):
    """pop up message box with header and message"""
    self.message_complete = QtWidgets.QMessageBox.information(self, header, message)

def next_window(self, window, close=True):
    """calls next window, closes current if True"""
    self.next_window_jump = window
    self.next_window_jump.show()
    if close == True:
        self.hide()


def dimensions(self):
    """gets current dimensions of window"""
    posx = self.geometry().x()
    posy = self.geometry().y()
    return posx, posy

def select_gml(self):
    """func to select file"""
    tup = QtWidgets.QFileDialog.getOpenFileName(self, 'Select .gml or .xml file', self.tr("*.gml;*.xml"))
    path = tup[0]
    if path.endswith('.gml') or path.endswith('.xml'):
        return path
    else:
        self.txtB_inPath.setText('')  
        messageBox(self, "Important", "Valid File not selected")
        return 0



def select_folder(self):
    """func to select folder"""
    dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
    if dirpath:
        return dirpath
    else:
        messageBox(self, "Important", "Valid Folder not selected")
        return 0


def new_search(self):
    """resetting data and gui"""
    # resetting gui
    self.textbox_gml.setText('')
    self.textbox_gml_folder.setText('')
    # en/disabling buttons
    self.btn_select_file.setEnabled(True)
    self.btn_select_folder.setEnabled(True)
    # self.btn_save.setEnabled(False)
    self.btn_reset.setEnabled(False)

