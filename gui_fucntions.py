from PySide6 import QtWidgets, QtGui, QtCore



def screenSizer(posx: int, posy: int, width: int, height: int, app: QtWidgets.QApplication) -> tuple[int, int, int, int, float]:
    """
    func to get size of screen and scale window dimensions accordingly
    returns posx, posy, width, height, sizefactor
    """
    sizefactor = round(app.primaryScreen().size().height()*0.001)              # factor for scaling window, depending on height
    posx *= sizefactor
    posy *= sizefactor
    width *= sizefactor
    height *= sizefactor
    return posx, posy, width, height, sizefactor


def windowSetup(self, posx: int, posy, width, height, title, winFac = 1) -> None:
    """func for loading icon, setting size and title"""
    try:                                                                            # try to load e3d Icon
        self.setWindowIcon(QtGui.QIcon(r'pictures\e3dIcon.png'))
    except:
        print('error finding file icon')
    self.setGeometry(posx, posy, width * winFac, height * winFac)                   # setting window size
    self.setFixedSize(width * winFac, height * winFac)                                                # fixing window size
    self.setWindowTitle(title)


def load_banner(self, path: str, sizefactor: float, banner_size: int = 150) -> None:
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


def close_application(self) -> None:
    """quit dialog, to confirm exiting"""
    choice = QtWidgets.QMessageBox.question(self, 'Attention!', 'Do you want to quit?',
                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if choice == QtWidgets.QMessageBox.Yes:
        QtCore.QCoreApplication.instance().quit()
    else:
        pass


def messageBox(self, header: str, message: str) -> None:
    """pop up message box with header and message"""
    self.message_complete = QtWidgets.QMessageBox.information(self, header, message)
